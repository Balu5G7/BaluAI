import os
import re
import requests
from google import genai
from PIL import Image

def route_llm(prompt: str, task_type: str = "general", image_path: str = None) -> tuple[str, str]:
    """
    Selects the best LLM provider based on task_type and falls back if key is missing or API errors out.
    task_type options: "coding", "reasoning", "research", "offline", "general"
    Returns a tuple: (response_text, model_name_used)
    """
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    claude_key = os.environ.get("CLAUDE_API_KEY", "") or os.environ.get("ANTHROPIC_API_KEY", "")
    ollama_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

    # Order of preference based on task_type
    preference_order = []
    
    if task_type == "coding":
        preference_order = ["claude", "gpt", "gemini", "ollama"]
    elif task_type == "reasoning":
        preference_order = ["gpt", "claude", "gemini", "ollama"]
    elif task_type == "research" or task_type == "vision":
        preference_order = ["gemini", "gpt", "claude", "ollama"]
    elif task_type == "offline":
        preference_order = ["ollama", "gemini"]
    else:
        preference_order = ["gemini", "gpt", "claude", "ollama"]

    # If an image is provided, we must use a vision-capable provider (Gemini or GPT-4o)
    if image_path:
        preference_order = ["gemini", "gpt", "ollama"]

    errors = []
    
    for provider in preference_order:
        try:
            if provider == "claude" and claude_key:
                from anthropic import Anthropic
                client = Anthropic(api_key=claude_key)
                response = client.messages.create(
                    model="claude-3-5-sonnet-latest",
                    max_tokens=2048,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text, "Claude 3.5 Sonnet"
                
            elif provider == "gpt" and openai_key:
                # We dynamically import openai to avoid import errors if not installed
                import openai
                client = openai.OpenAI(api_key=openai_key)
                model = "gpt-4o-mini" if task_type != "reasoning" else "gpt-4o"
                
                if image_path:
                    import base64
                    with open(image_path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    messages = [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_string}"}}
                        ]
                    }]
                else:
                    messages = [{"role": "user", "content": prompt}]
                    
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=2048
                )
                return response.choices[0].message.content, f"GPT ({model})"

            elif provider == "gemini" and gemini_key:
                client = genai.Client(api_key=gemini_key)
                model = 'gemini-2.5-flash'
                
                if image_path:
                    img = Image.open(image_path)
                    contents = [prompt, img]
                else:
                    contents = prompt
                    
                response = client.models.generate_content(
                    model=model,
                    contents=contents
                )
                return response.text, "Gemini 2.5 Flash"

            elif provider == "ollama":
                # Check if Ollama is running
                try:
                    resp = requests.get(f"{ollama_url}/api/tags", timeout=2)
                    if resp.status_code == 200:
                        # Find an installed model, default to llama3 or codegemma
                        models_data = resp.json()
                        models = [m["name"] for m in models_data.get("models", [])]
                        
                        target_model = "llama3"
                        if task_type == "coding" and any("code" in m for m in models):
                            target_model = [m for m in models if "code" in m][0]
                        elif models:
                            target_model = models[0]
                            
                        # Post generate prompt
                        post_data = {
                            "model": target_model,
                            "prompt": prompt,
                            "stream": False
                        }
                        gen_resp = requests.post(f"{ollama_url}/api/generate", json=post_data, timeout=30)
                        if gen_resp.status_code == 200:
                            return gen_resp.json().get("response", ""), f"Ollama ({target_model})"
                except Exception as e:
                    errors.append(f"Ollama offline: {e}")
                    
        except Exception as e:
            errors.append(f"{provider.upper()} API Error: {e}")

    # Ultimate fallback: if Gemini key is available, try it as it is our primary config
    if gemini_key:
        try:
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            return response.text, "Gemini 2.5 Flash (Fallback)"
        except Exception as e:
            errors.append(f"Gemini fallback failed: {e}")

    error_summary = "; ".join(errors)
    return f"Sir, all configured LLM APIs failed. Errors: {error_summary}", "Offline / Error"
