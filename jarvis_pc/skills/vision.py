import pyautogui
import datetime
import os
import cv2
from pathlib import Path

SCREENSHOTS_DIR = Path.home() / "JARVIS_Screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)

def take_screenshot() -> str:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = SCREENSHOTS_DIR / f"jarvis_{timestamp}.png"
    img = pyautogui.screenshot()
    img.save(str(filename))
    return str(filename)

def capture_webcam_image() -> str:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = SCREENSHOTS_DIR / f"jarvis_cam_{timestamp}.jpg"
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return ""
    
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        cv2.imwrite(str(filename), frame)
        return str(filename)
    return ""

def get_screen_size() -> dict:
    size = pyautogui.size()
    return {"width": size.width, "height": size.height}

def click_at(x: int, y: int):
    pyautogui.click(x, y)

def type_text(text: str):
    pyautogui.typewrite(text, interval=0.05)

def press_key(key: str):
    pyautogui.press(key)

def hotkey(*keys):
    pyautogui.hotkey(*keys)
