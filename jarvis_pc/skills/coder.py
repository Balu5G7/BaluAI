import subprocess
from pathlib import Path
from core.llm import get_jarvis_response
import re

def run_and_debug_script(speak_func) -> str:
    desktop = Path.home() / "Desktop" / "jarvis_script.py"
    if not desktop.exists():
        return "I could not find the script on your desktop, sir."
        
    speak_func("Running the script now, sir.")
    
    for attempt in range(3):
        try:
            # Run the script and capture output/errors
            result = subprocess.run(
                ["python", str(desktop)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("Script Output:", result.stdout)
                return "The script executed successfully, sir."
            else:
                speak_func(f"The script failed with an error. Attempting to self-heal, attempt {attempt + 1} of 3.")
                error_msg = result.stderr
                print("Script Error:", error_msg)
                
                with open(desktop, "r", encoding="utf-8") as f:
                    old_code = f.read()
                    
                prompt = (
                    f"The following Python script threw an error when executed.\n\n"
                    f"Code:\n```python\n{old_code}\n```\n\n"
                    f"Error Traceback:\n{error_msg}\n\n"
                    f"Please fix the error and output ONLY the complete fixed python code inside a ```python block."
                )
                
                code_response = get_jarvis_response(prompt)
                
                match = re.search(r"```python(.*?)```", code_response, re.DOTALL)
                if match:
                    fixed_code = match.group(1).strip()
                    with open(desktop, "w", encoding="utf-8") as f:
                        f.write(fixed_code)
                    speak_func("I have rewritten the code. Trying again.")
                else:
                    return "I was unable to generate a fix for the code."
                    
        except subprocess.TimeoutExpired:
            return "The script took too long to execute and timed out, sir."
        except Exception as e:
            return f"Failed to run the script: {e}"
            
    return "I am sorry sir, I could not fix the script after 3 attempts."
