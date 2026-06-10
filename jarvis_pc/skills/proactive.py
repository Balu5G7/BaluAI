import time
import threading
from skills.vision import capture_webcam_image
from core.llm import analyze_image

def proactive_monitor(speak_func):
    """
    Runs in the background. Every 30 minutes, it silently checks the webcam
    to see if the user is sitting at the desk and their posture.
    If posture is bad, Jarvis will speak up.
    """
    print("[Proactive] Monitor started. Will check every 30 minutes.")
    while True:
        time.sleep(1800)  # Wait 30 minutes (1800 seconds)
        
        try:
            print("[Proactive] Checking user presence and posture...")
            img_path = capture_webcam_image()
            if not img_path:
                continue
                
            prompt = (
                "You are Jarvis, a proactive AI assistant. Look at this webcam image of the user. "
                "1. If the user is not visible, reply exactly 'NO_USER'. "
                "2. If the user is slouching badly or has poor posture, give a short, polite verbal warning (e.g., 'Sir, your posture is deteriorating. Please sit up straight.'). "
                "3. If their posture is fine, reply exactly 'OK'. "
                "Keep warnings under 2 sentences."
            )
            
            response = analyze_image(img_path, prompt)
            response_clean = response.strip()
            
            if response_clean not in ["NO_USER", "OK"]:
                print(f"[Proactive] Triggering speech: {response_clean}")
                speak_func(response_clean)
                
        except Exception as e:
            print(f"[Proactive] Error during check: {e}")

def start_proactive_thread(speak_func):
    t = threading.Thread(target=proactive_monitor, args=(speak_func,), daemon=True)
    t.start()
