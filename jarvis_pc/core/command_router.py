"""
Command Router - Parses user voice commands and routes them to the correct skill.
"""
import re
import os
import time
import threading
import datetime

from skills.app_manager import open_application, close_application
from skills.system_ops import shutdown_pc, restart_pc, sleep_pc, set_volume, get_system_status
from skills.file_ops import create_file, read_file, delete_file, move_file, list_directory, create_folder
from skills.vision import take_screenshot, capture_webcam_image
from skills.web_search import search_google, search_youtube, open_url
from core.llm import get_jarvis_response, analyze_image
from core.memory import MemoryDB

import pyperclip
import pywhatkit

from pathlib import Path

from skills.email_ops import read_latest_emails
from skills.coder import run_and_debug_script

# Memory Database
db = MemoryDB()

# Words that are too short/noisy to bother sending to the LLM
NOISE_WORDS = {"jarvis", "hey", "hey jarvis", "um", "uh", "ok", "okay", "hmm"}

# --- Alarm State ---
_alarm_pending = False
_alarm_time = None
def _parse_time(text: str):
    """Try to parse a time string."""
    word_to_num = {
        "zero": "0", "one": "1", "two": "2",
        "three": "3", "four": "4", "five": "5",
        "six": "6", "seven": "7", "eight": "8",
        "nine": "9", "ten": "10", "eleven": "11",
        "twelve": "12", "thirty": "30"
    }

    t = text.lower()

    for word, num in word_to_num.items():
        t = t.replace(word, num)

    match = re.search(r"(\d{1,2})[:\s](\d{2})\s*(am|pm)?", t)

    if match:
        hour, minute, meridiem = match.group(1), match.group(2), match.group(3) or ""
        return f"{hour}:{minute} {meridiem}".strip()

    match = re.search(r"(\d{1,2})\s*(am|pm)", t)

    if match:
        hour, meridiem = match.group(1), match.group(2)
        return f"{hour}:00 {meridiem}"

    return None

def _fire_alarm(alarm_label: str, speak_func):
    """Background thread that rings the alarm at the correct time."""
    import winsound
    speak_func(f"Alarm set for {alarm_label}, sir. I will alert you on time.")
    while True:
        now = datetime.datetime.now().strftime("%I:%M %p").lstrip("0").lower()
        target = alarm_label.lower().lstrip("0")
        if now == target:
            speak_func("Sir, your alarm is ringing. Wake up!")
            # Beep 5 times
            for _ in range(5):
                try:
                    winsound.Beep(1000, 800)
                    time.sleep(0.4)
                except Exception:
                    pass
            break
        time.sleep(30)  # check every 30 seconds


# --- Confirmation Guard ---
DANGEROUS_KEYWORDS = ["shutdown", "shut down", "restart", "reboot", "delete", "remove"]

def requires_confirmation(command: str) -> bool:
    return any(kw in command for kw in DANGEROUS_KEYWORDS)


def route_command(command: str, speak_func, confirm_func=None) -> str:
    """
    Routes a command string to the appropriate skill or LLM.
    Returns a response string.
    """
    c = command.lower().strip()

    # --- Guard: ignore noise / wake-word echoes ---
    if not c or c in NOISE_WORDS:
        return ""

    # --- Cancel/Stop Command ---
    if c in ["stop", "cancel", "jarvis stop"] or "never mind" in c or "cancel that" in c:
        if speak_func: speak_func("Command cancelled, sir.")
        return ""

    # --- Alarm: step 1 - user asks to set an alarm ---
    if re.search(r"set\s+(an?\s+)?alarm", c) or "wake me up" in c:
        return "At what time would you like me to set the alarm, sir?"

    # --- Alarm: step 2 - user provides a time (follow-up turn) ---
    # Detect if this looks like a time answer (short input with numbers/am/pm)
    time_val = _parse_time(c)
    if time_val and len(c.split()) <= 6:  # short phrase = likely a time answer
        t = threading.Thread(target=_fire_alarm, args=(time_val, speak_func), daemon=True)
        t.start()
        return ""  # _fire_alarm will speak the confirmation itself

    # --- App Control ---
    if match := re.search(r"open (.+)", c):
        app = match.group(1).strip()
        open_application(app)
        return f"Opening {app}, sir."

    if match := re.search(r"close (.+)", c):
        app = match.group(1).strip()
        close_application(app)
        return f"Closing {app}."

    # --- Web Search ---
    if match := re.search(r"search (?:google )?(?:for )?(.+)", c):
        query = match.group(1)
        search_google(query)
        return f"Searching Google for {query}."

    if match := re.search(r"(?:search )?youtube (?:for )?(.+)", c):
        query = match.group(1)
        search_youtube(query)
        return f"Searching YouTube for {query}."

    # --- Screenshots ---
    if "screenshot" in c or "take a picture" in c:
        path = take_screenshot()
        return f"Screenshot saved to {path}, sir."

    # --- Volume ---
    if match := re.search(r"(?:set )?volume (?:to )?(\d+)", c):
        level = int(match.group(1))
        set_volume(level)
        return f"Volume set to {level} percent."

    if "mute" in c:
        set_volume(0)
        return "System muted."

    # --- File Operations ---
    if match := re.search(r"list (?:files in |directory )?(.+)", c):
        dirpath = match.group(1).strip()
        result = list_directory(dirpath)
        return result

    if match := re.search(r"create folder (.+)", c):
        folder = match.group(1).strip()
        return create_folder(folder)

    if match := re.search(r"create file (.+)", c):
        filepath = match.group(1).strip()
        result = create_file(filepath)
        return result

    # --- Folder Shortcuts ---
    if "open downloads" in c:
        os.startfile(os.path.join(os.path.expanduser("~"), "Downloads"))
        return "Opening Downloads folder, sir."

    if "open documents" in c:
        os.startfile(os.path.join(os.path.expanduser("~"), "Documents"))
        return "Opening Documents folder, sir."

    if "open desktop" in c:
        os.startfile(os.path.join(os.path.expanduser("~"), "Desktop"))
        return "Opening Desktop, sir."

    if match := re.search(r"read file (.+)", c):
        filepath = match.group(1).strip()
        return read_file(filepath)

    if "system status" in c or "battery" in c or "how are you" in c:
        return get_system_status()

    # --- Screen & Clipboard Analysis ---
    screen_triggers = ["read my screen", "what is on my screen", "explain this", "what am i looking at", "summarize this screen", "what is this code"]
    if any(t in c for t in screen_triggers):
        if speak_func: speak_func("Analyzing your screen, sir.")
        img_path = take_screenshot()
        return analyze_image(img_path, "You are Jarvis. Look at the attached screenshot of the user's screen. If they asked to 'explain this code' or 'what is this', focus on the main content visible (like code, an article, or an image) and explain it clearly and concisely.")

    if "read clipboard" in c or "summarize this" in c:
        text = pyperclip.paste()
        if not text:
            return "The clipboard is empty, sir."
        if speak_func: speak_func("Reading clipboard, sir.")
        return get_jarvis_response(f"Please summarize this copied text: {text}")

    # --- Programmer JARVIS ---
    if "write a python script" in c or "write code" in c:
        if speak_func: speak_func("Generating code, sir.")
        code_response = get_jarvis_response(c + " Output ONLY valid python code inside a ```python block.")
        match = re.search(r"```python(.*?)```", code_response, re.DOTALL)
        if match:
            code = match.group(1).strip()
            desktop = Path.home() / "Desktop" / "jarvis_script.py"
            with open(desktop, "w", encoding="utf-8") as f:
                f.write(code)
            return f"I have written the script and saved it to your Desktop as jarvis_script.py."
        return "I could not generate valid code for that request."

    if "run the script" in c or "execute the script" in c:
        return run_and_debug_script(speak_func)

    # --- Media & Automation ---
    if "play " in c and " on youtube" in c:
        song = c.split("play ")[1].replace(" on youtube", "").strip()
        if speak_func: speak_func(f"Playing {song} on YouTube.")
        pywhatkit.playonyt(song)
        return ""

    if "send whatsapp to" in c:
        match = re.search(r"send whatsapp to (\+?\d+) saying (.*)", c)
        if match:
            number = match.group(1)
            msg = match.group(2)
            if speak_func: speak_func("Sending WhatsApp message, sir.")
            pywhatkit.sendwhatmsg_instantly(number, msg, wait_time=15, tab_close=True)
            return "Message sent successfully."
        return "Please specify the number and the message clearly. Example: 'send whatsapp to +919876543210 saying hello'."

    if "read my emails" in c or "check my email" in c or "any unread emails" in c:
        if speak_func: speak_func("Checking your inbox, sir.")
        return read_latest_emails()

    # --- Vision / Object Scanning ---
    if "scan this" in c or "what is this" in c or "what am i holding" in c:
        if speak_func:
            speak_func("Scanning the object now, sir. Please hold it steady.")
        
        img_path = capture_webcam_image()
        if img_path:
            return analyze_image(img_path, "You are JARVIS. Describe the main object in this image briefly and naturally.")
        else:
            return "I am unable to access the camera, sir."

    # --- Dangerous System Ops (need confirmation) ---
    if "shutdown" in c or "shut down" in c:
        if confirm_func and confirm_func("Are you sure you want to shut down the PC?"):
            shutdown_pc()
            return "Shutting down in 5 seconds, sir."
        return "Shutdown cancelled."

    if "restart" in c or "reboot" in c:
        if confirm_func and confirm_func("Are you sure you want to restart the PC?"):
            restart_pc()
            return "Restarting in 5 seconds, sir."
        return "Restart cancelled."

    # --- PC Sleep (distinct from "sleep jarvis" which puts JARVIS to sleep mode) ---
    sleep_triggers = ["sleep pc", "sleep the pc", "put pc to sleep", "put the pc to sleep",
                       "put computer to sleep", "sleep the computer", "hibernate",
                       "sleep mode", "go to sleep mode", "pc sleep"]
    if any(t in c for t in sleep_triggers):
        sleep_pc()
        return "Putting the system to sleep, sir."

    if match := re.search(r"delete file (.+)", c):
        filepath = match.group(1).strip()
        if confirm_func and confirm_func(f"Confirm deletion of {filepath}?"):
            return delete_file(filepath)
        return "Deletion cancelled."
        # --- Memory Commands ---

    if c.startswith("remember "):
        data = c.replace("remember ", "").strip()

        if " is " in data:
            key, value = data.split(" is ", 1)

            db.remember_fact(key.strip(), value.strip())

            return f"I will remember that {key.strip()} is {value.strip()}, sir."

    if c.startswith("what is my "):
        key = c.replace("what is my ", "").strip()

        value = db.recall_fact(key)

        if value:
            return f"Your {key} is {value}, sir."

        return f"I do not know your {key} yet, sir."

    if c == "show memories":
        memories = db.list_memories()

        if memories:
            return "Stored memories: " + ", ".join(memories)

        return "I have no memories stored yet, sir."

    # --- Conversation / Fallback to Claude ---
    print(f"[DEBUG] No skill matched — falling back to LLM with: '{command}'")
    llm_response = get_jarvis_response(command)
    print(f"[DEBUG] LLM returned: '{llm_response[:100] if llm_response else '(empty)'}'")
    return llm_response