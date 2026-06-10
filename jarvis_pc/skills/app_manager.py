import subprocess
import webbrowser
from AppOpener import open as app_open
from AppOpener import close as app_close

APP_PATHS = {
    "notepad": "notepad.exe",
    "brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    "vscode": r"C:\Users\balup\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "vs code": r"C:\Users\balup\AppData\Local\Programs\Microsoft VS Code\Code.exe",
}

SITES = {
    "whatsapp": "https://web.whatsapp.com",
    "youtube": "https://youtube.com",
    "gmail": "https://mail.google.com",
    "chatgpt": "https://chatgpt.com",
    "instagram": "https://instagram.com",
}

def open_application(app_name: str):
    print(f"Opening {app_name}")
    key = app_name.lower().strip()

    # --- Website shortcuts ---
    for site, url in SITES.items():
        if site in key:
            webbrowser.open(url)
            return

    if key in APP_PATHS:
        subprocess.Popen(APP_PATHS[key])
    else:
        app_open(app_name, match_closest=True)

def close_application(app_name: str):
    print(f"Closing {app_name}")
    app_close(app_name, match_closest=True)
