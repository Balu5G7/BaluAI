import cv2
import os

def capture_master_face():
    print("Opening webcam. Please look directly into the camera...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
        
    print("Press SPACE to take the photo, or ESC to cancel.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
            
        cv2.imshow("Capture Master Face (Press SPACE to save)", frame)
        
        k = cv2.waitKey(1)
        if k % 256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k % 256 == 32:
            # SPACE pressed
            # Save it directly into the skills folder where it's needed
            save_path = os.path.join("skills", "owner.jpg")
            cv2.imwrite(save_path, frame)
            print(f"Success! Your face has been saved as '{save_path}'.")
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_master_face()
