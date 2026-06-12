import os
import subprocess
import shutil
from pathlib import Path

class AutomationAgent:
    def __init__(self):
        pass

    def open_app(self, app_name: str) -> str:
        """Launches an application by name."""
        try:
            # Common shortcuts
            apps = {
                "notepad": "notepad.exe",
                "chrome": "chrome.exe",
                "calc": "calc.exe",
                "explorer": "explorer.exe",
                "cmd": "cmd.exe",
                "powershell": "powershell.exe"
            }
            target = apps.get(app_name.lower(), app_name)
            subprocess.Popen(target, shell=True)
            return f"Sir, I have launched {app_name}."
        except Exception as e:
            return f"Failed to open application {app_name}: {e}"

    def close_app(self, app_name: str) -> str:
        """Kills an application process."""
        try:
            cmd = f"taskkill /f /im {app_name}.exe"
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                return f"Sir, I have closed {app_name}."
            return f"Could not find or close process {app_name}."
        except Exception as e:
            return f"Error closing {app_name}: {e}"

    def control_volume(self, action: str) -> str:
        """Controls system volume using WScript.Shell sendkeys in PowerShell."""
        action = action.lower()
        try:
            # Action options: "up", "down", "mute"
            if action == "up":
                cmd = "powershell -Command \"(New-Object -ComObject WScript.Shell).SendKeys([char]175)\""
            elif action == "down":
                cmd = "powershell -Command \"(New-Object -ComObject WScript.Shell).SendKeys([char]174)\""
            elif action == "mute":
                cmd = "powershell -Command \"(New-Object -ComObject WScript.Shell).SendKeys([char]173)\""
            else:
                return "Unknown volume command, sir."
                
            subprocess.run(cmd, shell=True)
            return f"Sir, volume adjusted: {action}"
        except Exception as e:
            return f"Error adjusting volume: {e}"

    def shutdown_pc(self) -> str:
        subprocess.run("shutdown /s /t 5", shell=True)
        return "Shutting down system in 5 seconds, sir."

    def restart_pc(self) -> str:
        subprocess.run("shutdown /r /t 5", shell=True)
        return "Restarting system in 5 seconds, sir."

    def sleep_pc(self) -> str:
        subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
        return "Putting system to sleep, sir."

    # File actions
    def create_file(self, path: str, content: str = "") -> str:
        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
            return f"File created successfully at {p.absolute()}"
        except Exception as e:
            return f"Error creating file: {e}"

    def delete_file(self, path: str) -> str:
        try:
            p = Path(path)
            if p.exists():
                if p.is_dir():
                    shutil.rmtree(p)
                else:
                    p.unlink()
                return f"Successfully deleted {p.absolute()}"
            return f"File not found at {path}"
        except Exception as e:
            return f"Error deleting file: {e}"

    def move_file(self, src: str, dst: str) -> str:
        try:
            shutil.move(src, dst)
            return f"Moved file from {src} to {dst}"
        except Exception as e:
            return f"Error moving file: {e}"
