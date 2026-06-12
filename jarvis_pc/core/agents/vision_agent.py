import os
import cv2
from pathlib import Path
from skills.vision import take_screenshot, capture_webcam_image
from core.router.llm_router import route_llm

class VisionAgent:
    def __init__(self):
        pass

    def read_screen(self, query: str = None) -> str:
        """Captures a screenshot and uses vision LLM to explain what's on the screen."""
        img_path = take_screenshot()
        if not img_path:
            return "Sir, I failed to capture a screenshot of your screen."
            
        prompt = "You are JARVIS. Look at the attached screenshot of the user's screen. "
        if query:
            prompt += f"The user asked: {query}. Focus specifically on answering their question based on the image content."
        else:
            prompt += "Explain what is on the user's screen clearly and concisely."
            
        response, model = route_llm(prompt, task_type="vision", image_path=img_path)
        return f"[Model: {model}]\n{response}"

    def explain_error(self) -> str:
        """Captures a screenshot, finds any visible error tracebacks or error dialogues, and explains them."""
        img_path = take_screenshot()
        if not img_path:
            return "Sir, I failed to capture a screenshot to examine the error."
            
        prompt = """
You are JARVIS, a senior debugger. Look at the attached screenshot of the user's screen.
Locate any visible errors, tracebacks, terminal exceptions, compiler warnings, or dialogue errors.
Explain what is causing the error and how the user can fix it step-by-step.
"""
        response, model = route_llm(prompt, task_type="vision", image_path=img_path)
        return f"[Model: {model}]\n{response}"

    def analyze_webcam_feed(self, query: str) -> str:
        """Captures a frame from the webcam and explains what is in it."""
        img_path = capture_webcam_image()
        if not img_path:
            return "Sir, I cannot access the webcam at the moment."
            
        response, model = route_llm(query, task_type="vision", image_path=img_path)
        return f"[Model: {model}]\n{response}"

    def recognize_person(self) -> str:
        """Uses facial detection and/or DeepFace authentication to check who is in front of the camera."""
        img_path = capture_webcam_image()
        if not img_path:
            return "Sir, I cannot access the webcam to verify your identity."
            
        # Try DeepFace or fall back to OpenCV cascade + Vision LLM
        try:
            from skills.security import perform_security_check
            is_owner = perform_security_check()
            if is_owner:
                return "Biometric verification successful. Welcome back, Balu."
        except Exception:
            pass
            
        prompt = "Describe the person visible in the webcam image. State their approximate age, gender, and current expression. If it is Balu, address him as master."
        response, model = route_llm(prompt, task_type="vision", image_path=img_path)
        return f"[Model: {model}]\n{response}"

    def analyze_local_image(self, file_path: str, prompt: str = None) -> str:
        """Analyzes a local image file using the vision LLM."""
        if not os.path.exists(file_path):
            return f"Sir, I could not find the image file at {file_path}."
            
        if not prompt:
            prompt = "Describe what is in this image clearly and concisely."
            
        response, model = route_llm(prompt, task_type="vision", image_path=file_path)
        return f"[Model: {model}]\n{response}"
