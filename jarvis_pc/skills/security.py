import cv2
import ctypes
import os

# Suppress TensorFlow warnings from DeepFace
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

def perform_security_check() -> bool:
    print("[Security] Performing Facial Scan...")
    
    owner_path = "owner.jpg"
    if not os.path.exists(owner_path):
        owner_path = os.path.join("skills", "owner.jpg")
        
    if not os.path.exists(owner_path):
        print(f"[Security] owner.jpg not found in root or skills/. Skipping security check.")
        return True
        
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[Security] Webcam not found. Skipping check.")
        return True
        
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("[Security] Failed to capture image. Skipping check.")
        return True
        
    cv2.imwrite("temp_login.jpg", frame)
    
    try:
        from deepface import DeepFace
        # Compare webcam frame with master owner.jpg
        result = DeepFace.verify(img1_path="temp_login.jpg", img2_path=owner_path, enforce_detection=False)
        verified = result.get('verified', False)
        
        try:
            if os.path.exists("temp_login.jpg"):
                os.remove("temp_login.jpg")
        except: pass
            
        if verified:
            return True
        else:
            return False
    except Exception as e:
        print("[Security] DeepFace error:", e)
        return False # Deny access if verification fails or crashes
        
def lock_system():
    """Immediately locks the Windows session."""
    ctypes.windll.user32.LockWorkStation()
