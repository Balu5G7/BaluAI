"""
JARVIS FastAPI Server - Handles all mobile-to-PC communication.
Endpoints: REST for status/commands, WebSocket for live chat.
"""
import asyncio
import base64
import os
from pathlib import Path
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Header
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.command_router import route_command
from core.memory import MemoryDB
from skills.vision import take_screenshot, get_screen_size

app = FastAPI(title="JARVIS Server", version="1.0")

# Allow all origins for local network use
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db = MemoryDB()

# Simple token auth - set JARVIS_TOKEN in .env
JARVIS_TOKEN = os.environ.get("JARVIS_TOKEN", "jarvis-secret-token-2024")

def verify_token(authorization: str = Header(None)):
    if authorization != f"Bearer {JARVIS_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")


# --- Models ---
class CommandRequest(BaseModel):
    command: str

class MessageOut(BaseModel):
    role: str
    content: str


# --- REST Endpoints ---

@app.get("/status")
def get_status():
    """PC health check endpoint."""
    import platform, psutil
    return {
        "status": "online",
        "platform": platform.system(),
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "screen": get_screen_size(),
    }


@app.post("/command")
def send_command(req: CommandRequest, authorization: str = Header(None)):
    verify_token(authorization)
    response = route_command(req.command, speak_func=print)
    return {"response": response}


@app.get("/history")
def get_history(authorization: str = Header(None)):
    verify_token(authorization)
    history = db.get_history(limit=20)
    return {"history": history}


@app.delete("/history")
def clear_history(authorization: str = Header(None)):
    verify_token(authorization)
    db.clear_history()
    return {"message": "History cleared."}


@app.get("/screenshot")
def get_screenshot(authorization: str = Header(None)):
    verify_token(authorization)
    path = take_screenshot()
    return FileResponse(path, media_type="image/png")


@app.post("/transfer")
async def receive_file(filename: str, content: str, authorization: str = Header(None)):
    """Receive a base64-encoded file from mobile."""
    verify_token(authorization)
    save_path = Path.home() / "JARVIS_Transfers" / filename
    save_path.parent.mkdir(exist_ok=True)
    save_path.write_bytes(base64.b64decode(content))
    return {"message": f"File saved to {save_path}"}


# --- WebSocket for Live Voice Chat ---
class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, message: str):
        for connection in self.active:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            # data is the user's voice command text
            response = route_command(data, speak_func=print)
            await ws.send_text(response)
    except WebSocketDisconnect:
        manager.disconnect(ws)
