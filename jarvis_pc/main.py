"""
JARVIS Main Entry Point.
- Starts the FastAPI server on a background thread.
- Runs the wake-word voice loop on the main thread.
"""
import threading
import os
import sys
import psutil
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import uvicorn
from api.server import app
from core.stt_tts import speak, listen_for_command
from core.command_router import route_command
from gui import root, update_status, set_animation_state
from skills.security import perform_security_check, lock_system

WAKE_WORDS = ["hey jarvis", "jarvis", "hey jervis", "jarves"]
EXIT_PHRASES = ["goodbye jarvis", "exit jarvis", "shutdown jarvis", "sleep jarvis"]


def start_api_server():
    """Runs the FastAPI server in a daemon thread."""
    port = int(os.environ.get("JARVIS_PORT", 8765))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")


def confirm_action(prompt: str) -> bool:
    """Ask for verbal confirmation before dangerous operations."""
    speak(f"{prompt} Say yes to confirm.")
    response = listen_for_command()
    return "yes" in response

def system_monitor_loop():
    """Runs continuously in the background and proactively speaks if something is wrong."""
    alerted = False
    while True:
        try:
            battery = psutil.sensors_battery()
            if battery and battery.percent < 20 and not battery.power_plugged and not alerted:
                speak(f"Pardon the interruption sir, but your battery is running extremely low at {battery.percent} percent. Please plug in the charger.")
                alerted = True
            elif battery and battery.power_plugged:
                alerted = False
        except Exception:
            pass
        time.sleep(300)  # Check every 5 minutes

# How many follow-up turns JARVIS will handle before going back to sleep
MAX_FOLLOWUP_TURNS = 3


def voice_loop():
    """Runs the voice command loop in a background thread.
    Stays in sleep mode until wake word is detected.
    After activation, it stays continuously awake until told to sleep.
    """
    speak("JARVIS online. All systems operational. Say Jarvis to activate.")

    is_awake = False
    command = ""

    while True:
        if not is_awake:
            # --- Sleep Mode: Wait for wake word ---
            set_animation_state("idle")
            update_status("💤 Sleep Mode — Say 'Jarvis'")
            heard = listen_for_command()

            if not heard:
                continue

            print(f"[DEBUG] Heard in sleep mode: '{heard}'")

            # Check exit commands even in sleep mode
            if any(phrase in heard for phrase in EXIT_PHRASES):
                speak("Shutting down JARVIS. Goodbye, sir.")
                root.quit()
                sys.exit(0)

            # Check for wake word
            wake_detected = False
            embedded_command = ""
            for ww in WAKE_WORDS:
                if ww in heard:
                    wake_detected = True
                    # Extract any command embedded after the wake word
                    remaining = heard.replace(ww, "").strip()
                    if remaining and len(remaining) > 2:
                        embedded_command = remaining
                    break

            if not wake_detected:
                print(f"[DEBUG] No wake word found in: '{heard}'")
                continue

            print("[DEBUG] ✅ Wake word detected! Activating...")
            is_awake = True
            
            if embedded_command:
                print(f"[DEBUG] Embedded command found: '{embedded_command}'")
                command = embedded_command
            else:
                speak("Yes sir, I'm listening.")
                continue

        else:
            # --- Activated Mode: Continuous Listening ---
            set_animation_state("listening")
            update_status("🟢 Activated — Listening for command...")
            
            # If we don't have a command carried over from wake word
            if not command:
                command = listen_for_command()

            if not command:
                print("[DEBUG] No command received after activation.")
                continue

            print(f"[DEBUG] Processing command: '{command}'")

            # Check for sleep command explicitly
            if any(phrase in command for phrase in EXIT_PHRASES):
                if "sleep" in command:
                    speak("Going back to sleep, sir. Say Jarvis to wake me up.")
                    is_awake = False
                    command = ""
                    continue
                else:
                    speak("Shutting down JARVIS. Goodbye, sir.")
                    root.quit()
                    sys.exit(0)

            set_animation_state("processing")
            update_status(f"⚙️ Processing: {command[:40]}...")
            
            response = route_command(command, speak_func=speak, confirm_func=confirm_action)

            if response:
                speak(response)
            else:
                print("[DEBUG] Empty response from router.")

            # Clear command so next iteration listens again
            command = ""


def main():
    print("=" * 50)
    print("  JARVIS AI ASSISTANT - Starting Up")
    print("=" * 50)

    speak("System starting up. Welcome back, sir.")

    # Start API server in background thread
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()

    port = int(os.environ.get("JARVIS_PORT", 8765))
    print(f"[+] API Server running on http://0.0.0.0:{port}")
    print(f"[+] Wake words: '{', '.join(WAKE_WORDS).title()}'")
    print("[+] Listening for commands...")

    # Voice loop runs in background thread
    voice_thread = threading.Thread(target=voice_loop, daemon=True)
    voice_thread.start()

    # System monitor runs in background thread
    monitor_thread = threading.Thread(target=system_monitor_loop, daemon=True)
    monitor_thread.start()

    # Proactive AI monitor runs in background thread
    from skills.proactive import start_proactive_thread
    start_proactive_thread(speak)

    # Telegram Bot runs in background thread
    from skills.telegram_bot import start_telegram_thread
    start_telegram_thread()

    # GUI runs on main thread
    root.mainloop()


if __name__ == "__main__":
    main()
