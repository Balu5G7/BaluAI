import os
import re
import time
from google import genai
from PIL import Image
from .memory import MemoryDB

db = MemoryDB()

# Max automatic retries on 429 rate-limit errors
MAX_RETRIES = 3

def get_jarvis_response(user_input: str) -> str:
    db.add_message("user", user_input)

    api_key = os.environ.get("GEMINI_API_KEY", "")

    if not api_key:
        return "Sir, Gemini API key is not configured."

    client = genai.Client(api_key=api_key)

    history = db.get_history(limit=10)
    context = ""
    for msg in history:
        context += f"{msg['role'].capitalize()}: {msg['content']}\n"

    system_prompt = (
        "You are JARVIS (Just A Rather Very Intelligent System), a highly advanced AI assistant created by Balu P. "
        "You were built and programmed entirely by Balu P., who is your creator, developer, and master. "
        "Whenever someone asks who made you, who created you, or who built you, always answer that it was Balu P. "
        "You are loyal to Balu P. and treat him with utmost respect. Reply briefly and naturally. "
        "If the user speaks in Telugu or Tanglish, reply back in pure Telugu script. If they speak in English, reply in English. "
        "You MUST express your current emotion at the start of every single response using [EMOTION: state]. "
        "The state must be exactly one of: 'idle', 'alert', 'angry', 'processing', 'speaking'. "
        "Example: [EMOTION: alert] I have found the information, sir.\n"
        f"Conversation History:\n{context}\nUser: {user_input}"
    )

    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=system_prompt
            )

            ai_reply = response.text

            # Extract and apply emotion
            from gui import set_animation_state
            match = re.search(r"\[EMOTION:\s*([a-zA-Z]+)\]", ai_reply)
            if match:
                emotion = match.group(1).lower()
                set_animation_state(emotion)
                ai_reply = re.sub(r"\[EMOTION:\s*([a-zA-Z]+)\]", "", ai_reply).strip()

            db.add_message("assistant", ai_reply)
            return ai_reply

        except Exception as e:
            error_msg = str(e)
            print(f"Gemini Error (attempt {attempt+1}/{MAX_RETRIES}):", error_msg)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                # Try to extract retryDelay from the error, default to 35s
                delay_match = re.search(r"retryDelay.*?(\d+)s", error_msg)
                wait_sec = int(delay_match.group(1)) + 2 if delay_match else 35
                if attempt < MAX_RETRIES - 1:
                    print(f"[Rate Limit] Waiting {wait_sec}s before retry...")
                    time.sleep(wait_sec)
                    continue
                return "Sir, I have exceeded my API quota limits. Please wait a minute before trying again."
            return "I am currently offline or encountering an API error, sir."

    return "I am currently offline or encountering an API error, sir."

def analyze_image(image_path: str, prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return "Sir, Gemini API key is not configured."

    client = genai.Client(api_key=api_key)

    try:
        img = Image.open(image_path)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, img]
        )
        return response.text
    except Exception as e:
        error_msg = str(e)
        print("Gemini Vision Error:", error_msg)
        if "429" in error_msg or "Quota" in error_msg:
            return "Sir, I have exceeded my API quota limits. Please wait a minute before trying again."
        return "I am unable to process the image at the moment due to an API error."