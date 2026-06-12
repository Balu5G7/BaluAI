"""
Top-level process entry points for JARVIS background workers.
Must remain picklable for Windows multiprocessing spawn.
"""
import os
import sys
import time

import psutil
import uvicorn
from dotenv import load_dotenv
from multiprocessing import Queue, Event

from api.server import app
from core.command_router import route_command
from core.ipc import init_ipc, queue_speak, queue_status, queue_animation, queue_shutdown
from core.stt_tts import listen_for_command
from skills.proactive import proactive_monitor
from skills.telegram_bot import run_bot

WAKE_WORDS = ["hey jarvis", "jarvis", "hey jervis", "jarves"]
EXIT_PHRASES = ["goodbye jarvis", "exit jarvis", "shutdown jarvis", "sleep jarvis"]


def _load_env() -> None:
    load_dotenv()


def run_api_server() -> None:
    """Runs the FastAPI server in a dedicated process."""
    _load_env()
    port = int(os.environ.get("JARVIS_PORT", 8765))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")


def _confirm_action(prompt: str) -> bool:
    """Ask for verbal confirmation before dangerous operations."""
    queue_speak(f"{prompt} Say yes to confirm.")
    response = listen_for_command()
    return "yes" in response


def run_voice_loop(speak_queue: Queue, status_queue: Queue, speak_done: Event) -> None:
    """Runs the wake-word voice command loop in a dedicated process."""
    _load_env()
    init_ipc(speak_queue, status_queue, speak_done)

    queue_speak("JARVIS online. All systems operational. Say Jarvis to activate.")

    is_awake = False
    command = ""

    while True:
        if not is_awake:
            queue_animation("idle")
            queue_status("💤 Sleep Mode — Say 'Jarvis'")
            heard = listen_for_command()

            if not heard:
                continue

            print(f"[DEBUG] Heard in sleep mode: '{heard}'")

            if any(phrase in heard for phrase in EXIT_PHRASES):
                queue_speak("Shutting down JARVIS. Goodbye, sir.")
                queue_shutdown()
                sys.exit(0)

            wake_detected = False
            embedded_command = ""
            for ww in WAKE_WORDS:
                if ww in heard:
                    wake_detected = True
                    remaining = heard.replace(ww, "").strip()
                    if remaining and len(remaining) > 2:
                        embedded_command = remaining
                    break

            if not wake_detected:
                print(f"[DEBUG] No wake word found in: '{heard}'")
                continue

            print("[DEBUG] Wake word detected! Activating...")
            is_awake = True

            if embedded_command:
                print(f"[DEBUG] Embedded command found: '{embedded_command}'")
                command = embedded_command
            else:
                queue_speak("Yes sir, I'm listening.")
                continue

        else:
            queue_animation("listening")
            queue_status("🟢 Activated — Listening for command...")

            if not command:
                command = listen_for_command()

            if not command:
                print("[DEBUG] No command received after activation.")
                continue

            print(f"[DEBUG] Processing command: '{command}'")

            if any(phrase in command for phrase in EXIT_PHRASES):
                if "sleep" in command:
                    queue_speak("Going back to sleep, sir. Say Jarvis to wake me up.")
                    is_awake = False
                    command = ""
                    continue
                queue_speak("Shutting down JARVIS. Goodbye, sir.")
                queue_shutdown()
                sys.exit(0)

            queue_animation("processing")
            queue_status(f"⚙️ Processing: {command[:40]}...")

            response = route_command(
                command,
                speak_func=queue_speak,
                confirm_func=_confirm_action,
            )

            if response:
                queue_speak(response)
            else:
                print("[DEBUG] Empty response from router.")

            command = ""


def run_system_monitor(speak_queue: Queue, status_queue: Queue, speak_done: Event) -> None:
    """Runs battery monitoring in a dedicated process."""
    _load_env()
    init_ipc(speak_queue, status_queue, speak_done)

    alerted = False
    while True:
        try:
            battery = psutil.sensors_battery()
            if battery and battery.percent < 20 and not battery.power_plugged and not alerted:
                queue_speak(
                    f"Pardon the interruption sir, but your battery is running extremely low "
                    f"at {battery.percent} percent. Please plug in the charger."
                )
                alerted = True
            elif battery and battery.power_plugged:
                alerted = False
        except Exception:
            pass
        time.sleep(300)


def run_proactive_monitor(speak_queue: Queue, status_queue: Queue, speak_done: Event) -> None:
    """Runs posture/presence monitoring in a dedicated process."""
    _load_env()
    init_ipc(speak_queue, status_queue, speak_done)
    proactive_monitor(speak_func=queue_speak)


def run_telegram_bot() -> None:
    """Runs the Telegram remote-control bot in a dedicated process."""
    _load_env()
    run_bot()
