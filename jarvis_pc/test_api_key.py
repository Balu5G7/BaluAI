"""Quick test to check if Gemini API key is working."""
from dotenv import load_dotenv
load_dotenv()

import os
from google import genai

api_key = os.environ.get("GEMINI_API_KEY", "")
print(f"[Key] Using key: {api_key[:8]}...{api_key[-4:]}")
print(f"[Key] Length: {len(api_key)}")

try:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Say "Hello, I am JARVIS" in one line.'
    )
    print(f"[SUCCESS] Response: {response.text}")
except Exception as e:
    print(f"[ERROR] API call failed: {e}")
