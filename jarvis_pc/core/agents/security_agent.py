import os
import time
import subprocess
from pathlib import Path
from skills.vision import capture_webcam_image

class SecurityAgent:
    def __init__(self, log_path="security_activity.log"):
        self.log_path = Path(log_path)
        self.intruder_dir = Path.home() / "JARVIS_Intruders"
        self.intruder_dir.mkdir(exist_ok=True)

    def log_activity(self, action: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {action}\n")

    def run_face_auth(self) -> bool:
        """Runs security deepface auth check."""
        try:
            from skills.security import perform_security_check
            success = perform_security_check()
            self.log_activity(f"Face Auth check result: {success}")
            return success
        except Exception as e:
            self.log_activity(f"Face Auth failed with error: {e}")
            return False

    def trigger_intruder_detection(self) -> str:
        """Captures intruder photo, logs alert, and returns details."""
        img_path = capture_webcam_image()
        if img_path:
            save_path = self.intruder_dir / f"intruder_{int(time.time())}.jpg"
            try:
                import shutil
                shutil.copy(img_path, save_path)
                self.log_activity(f"INTRUDER ALERT! Photo saved to {save_path}")
                # Try Telegram Alert
                try:
                    from skills.telegram_bot import bot_app
                    # Optional notify code can go here
                except Exception:
                    pass
                return f"Intruder detected! Image captured and saved to {save_path}."
            except Exception as e:
                return f"Intruder detected! Capture failed: {e}"
        return "Intruder detected but camera capture failed."

    def lock_workstation(self) -> str:
        """Locks the Windows OS screen."""
        self.log_activity("Workstation locked by JARVIS")
        try:
            # Relaunches rundll32 User32.dll LockWorkStation
            subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
            return "Sir, I have locked your workstation."
        except Exception as e:
            return f"Error locking workstation: {e}"

    def get_security_status(self) -> str:
        if self.log_path.exists():
            with open(self.log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            recent_logs = "".join(lines[-10:])
            return f"Security Log Status:\n{recent_logs}"
        return "No security logs recorded yet, sir."
