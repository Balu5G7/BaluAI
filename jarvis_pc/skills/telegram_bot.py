import os
import asyncio
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from core.command_router import route_command

# Store the owner ID so only they can control Jarvis
OWNER_ID = None

def dummy_speak(text: str):
    """Used so Jarvis doesn't speak out loud on the PC when controlled from Telegram, unless desired."""
    print(f"[Telegram Bot] Jarvis would say: {text}")

def dummy_confirm(prompt: str) -> bool:
    """For dangerous commands via telegram, we just allow them or deny them. For now, deny."""
    print(f"[Telegram Bot] Blocked dangerous command needing confirmation: {prompt}")
    return False

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global OWNER_ID
    user_id = update.message.from_user.id
    
    if OWNER_ID is None:
        OWNER_ID = user_id
        await update.message.reply_text(f"Welcome sir! I have registered your ID ({OWNER_ID}) as the master. I will only accept commands from you.")
    elif user_id != OWNER_ID:
        await update.message.reply_text("Unauthorized access. You are not my master.")
    else:
        await update.message.reply_text("I am ready for your commands, sir.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if OWNER_ID is not None and user_id != OWNER_ID:
        return # Ignore others
        
    command = update.message.text
    print(f"[Telegram] Received: {command}")
    
    # Process through Jarvis's core brain
    response = route_command(command, speak_func=dummy_speak, confirm_func=dummy_confirm)
    
    if response:
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("Command executed or not understood.")

def run_bot():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("[Telegram Bot] No token found in .env. Skipping Telegram setup.")
        return
        
    print("[Telegram Bot] Starting...")
    
    # Needs a new event loop since it's running in a separate thread
    asyncio.set_event_loop(asyncio.new_event_loop())
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

def start_telegram_thread():
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()
