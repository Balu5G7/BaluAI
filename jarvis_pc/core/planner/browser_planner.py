import re
import time
from typing import Callable
from core.router.llm_router import route_llm
from skills.browser_tools import BrowserTools
from core.ipc import send_msg, MsgType

class BrowserPlanner:
    def __init__(self, headless=False):
        self.tools = BrowserTools(headless=headless)

    def set_animation(self, state: str):
        send_msg(MsgType.ANIMATION, state)

    def execute_goal(self, goal: str, speak_func: Callable = print) -> str:
        speak_func(f"Starting autonomous browser task: {goal}")
        self.set_animation("processing")
        self.tools.start()
        
        # Start at a neutral ground
        self.tools.goto("https://www.google.com")
        
        history = []
        max_steps = 15
        current_step = 0
        final_result = ""

        try:
            while current_step < max_steps:
                self.set_animation("browsing")
                time.sleep(1) # Small buffer for DOM to settle
                
                url = self.tools.page.url
                title = self.tools.page.title()
                dom_elements = self.tools.extract_dom()
                
                self.set_animation("processing")
                
                prompt = f"""
You are the JARVIS Autonomous Browser Agent Planner.
Goal: {goal}
Current URL: {url}
Page Title: {title}

Visible Interactive Elements:
{dom_elements}

Previous Action History:
{chr(10).join(history[-5:])}

Choose your NEXT SINGLE ACTION to progress towards the goal. Output ONLY ONE action matching the exact format:
1. GOTO: <url>
2. CLICK: <type> idx=<index> (e.g. CLICK: LINK idx=2)
3. TYPE: idx=<index> text="<text_to_type>"
4. PRESS: <key_name> (e.g. PRESS: Enter)
5. VISION_FALLBACK: <description> (If you cannot find the required element in the text DOM, use this to request a screenshot analysis)
6. FINISHED: <final_explanation_of_result>

Ensure your indices match the visible interactive elements listed above.
"""
                action_response, model = route_llm(prompt, task_type="reasoning")
                action_response = action_response.strip()
                history.append(f"Step {current_step+1}: {action_response}")
                print(f"[BrowserPlanner] {action_response}")

                if "FINISHED:" in action_response:
                    final_result = action_response.replace("FINISHED:", "").strip()
                    break
                    
                elif "GOTO:" in action_response:
                    target_url = action_response.replace("GOTO:", "").strip()
                    self.tools.goto(target_url)
                    
                elif "CLICK:" in action_response:
                    self.set_animation("clicking")
                    match_type = re.search(r"CLICK:\s*([A-Z]+)", action_response)
                    match_idx = re.search(r"idx=(\d+)", action_response)
                    if match_type and match_idx:
                        elem_type = match_type.group(1)
                        idx = int(match_idx.group(1))
                        res = self.tools.click_element(elem_type, idx)
                        history.append(f"Result: {res}")
                        
                elif "TYPE:" in action_response:
                    self.set_animation("typing")
                    match_idx = re.search(r"idx=(\d+)", action_response)
                    match_text = re.search(r'text="([^"]+)"', action_response)
                    if match_idx and match_text:
                        idx = int(match_idx.group(1))
                        text = match_text.group(1)
                        res = self.tools.type_text(idx, text)
                        history.append(f"Result: {res}")
                        
                elif "PRESS:" in action_response:
                    key = action_response.replace("PRESS:", "").strip()
                    self.tools.page.keyboard.press(key)
                    history.append(f"Result: Pressed {key}")

                elif "VISION_FALLBACK:" in action_response:
                    self.set_animation("processing")
                    speak_func("Standard DOM matching failed. Analyzing screen visually, sir.")
                    
                    screenshot_path = self.tools.take_screenshot()
                    if screenshot_path:
                        vision_prompt = f"Goal: {goal}\nLook at this screenshot. Describe exactly what I should do next, and if I need to click something, what text or icon is it?"
                        vision_res, _ = route_llm(vision_prompt, task_type="vision", image_path=screenshot_path)
                        history.append(f"Vision Feedback: {vision_res}")
                    else:
                        history.append("Vision Feedback: Failed to capture screenshot.")

                current_step += 1
                
            if not final_result:
                final_result = f"Task incomplete after {max_steps} steps."
                
        except Exception as ex:
            final_result = f"Error during browser execution: {ex}"
            
        finally:
            self.tools.close()
            self.set_animation("idle")
            
        return final_result
