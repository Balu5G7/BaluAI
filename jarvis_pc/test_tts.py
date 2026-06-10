import asyncio
import edge_tts

async def speak():
    communicate = edge_tts.Communicate(
        "Hello Balu. I am Jarvis.",
        voice="en-US-GuyNeural"
    )

    await communicate.save("jarvis.mp3")

asyncio.run(speak())
