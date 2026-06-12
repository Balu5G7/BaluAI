"""
JARVIS AI OS v3.0 — Main Entry Point.
Created by Balu P.

- Spawns background workers as separate processes.
- Main process owns the GUI (HUD) and TTS playback via IPC queues.
"""
import os
import sys
import time
from multiprocessing import Process, Queue, Event

from dotenv import load_dotenv

load_dotenv()

from core.stt_tts import speak
from core.workers import (
    run_api_server,
    run_voice_loop,
    run_system_monitor,
    run_proactive_monitor,
    run_telegram_bot,
)
from gui import root, start_ipc_polling

WAKE_WORDS = ["hey jarvis", "jarvis", "hey jervis", "jarves"]


def print_startup_banner():
    """Prints the JARVIS v3.0 startup sequence to console."""
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    print()
    print(f"{CYAN}{BOLD}{'=' * 52}{RESET}")
    print(f"{CYAN}{BOLD}       J.A.R.V.I.S.  AI  OS  v3.0{RESET}")
    print(f"{CYAN}{BOLD}       Created by Balu P.{RESET}")
    print(f"{CYAN}{BOLD}{'=' * 52}{RESET}")
    print()

    subsystems = [
        ("Brain",      "Multi-Agent Orchestrator"),
        ("Voice",      "Speech Recognition & TTS"),
        ("Memory",     "SQLite + Vector Memory"),
        ("Vision",     "Screen / Webcam / OCR"),
        ("Security",   "Auth / Intruder Detection"),
        ("Automation", "OS & App Control"),
        ("Telegram",   "Remote Bot Integration"),
        ("Browser",    "Playwright Web Agent"),
    ]

    for name, desc in subsystems:
        time.sleep(0.1)
        print(f"  {GREEN}[X]{RESET} {BOLD}{name:12s}{RESET} - {desc}")

    print()
    print(f"  {YELLOW}{BOLD}All Systems Operational.{RESET}")
    print(f"{CYAN}{BOLD}{'=' * 52}{RESET}")
    print()


def main():
    print_startup_banner()

    speak_q: Queue = Queue()
    status_q: Queue = Queue()
    speak_done: Event = Event()

    ipc_args = (speak_q, status_q, speak_done)

    processes = [
        Process(target=run_api_server, daemon=True),
        Process(target=run_voice_loop, args=ipc_args, daemon=True),
        Process(target=run_system_monitor, args=ipc_args, daemon=True),
        Process(target=run_proactive_monitor, args=ipc_args, daemon=True),
        Process(target=run_telegram_bot, daemon=True),
    ]

    for proc in processes:
        proc.start()

    port = int(os.environ.get("JARVIS_PORT", 8765))
    print(f"[+] API Server running on http://0.0.0.0:{port}")
    print(f"[+] Wake words: '{', '.join(WAKE_WORDS).title()}'")
    print("[+] Listening for commands...")

    speak("JARVIS v3 online. All systems operational. Welcome back, sir.")

    start_ipc_polling(speak_q, status_q, speak_done)
    root.mainloop()

    for proc in processes:
        if proc.is_alive():
            proc.terminate()
            proc.join(timeout=2)


if __name__ == "__main__":
    main()
