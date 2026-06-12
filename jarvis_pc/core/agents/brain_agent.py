from core.router.llm_router import route_llm
from core.agents.memory_agent import MemoryAgent
from core.agents.vision_agent import VisionAgent
from core.agents.coding_agent import CodingAgent
from core.agents.research_agent import ResearchAgent
from core.agents.automation_agent import AutomationAgent
from core.agents.security_agent import SecurityAgent
from core.agents.browser_agent import BrowserAgent
from core.planner.task_planner import TaskPlanner
from core.rag.rag_engine import RAGEngine

class BrainAgent:
    def __init__(self):
        self.memory_agent = MemoryAgent()
        self.vision_agent = VisionAgent()
        self.coding_agent = CodingAgent()
        self.research_agent = ResearchAgent()
        self.automation_agent = AutomationAgent()
        self.security_agent = SecurityAgent()
        self.browser_agent = BrowserAgent(headless=False) # Headed to let user watch
        self.planner = TaskPlanner()
        self.rag_engine = RAGEngine()

    def route_and_execute(self, command: str, speak_func=print) -> str:
        """Uses LLM classification to route commands to the specialized agent."""
        classification_prompt = f"""
Classify the following user command into one of these categories:
- MEMORY: Storing facts, recalling facts, forgetting facts, memory lists (e.g. remember X, recall Y, forget Z)
- VISION: Read screen, screenshot analysis, OCR, webcam analysis, who is in front of camera, what am I holding
- CODING: Write code, review code, fix bugs, refactor, Git commands, commits
- RESEARCH: General lookups, search facts, Wikipedia lookups, summarize article
- AUTOMATION: Volume up/down, shutdown, restart, sleep, open application, close application, create/delete files
- SECURITY: Logs, locks, intruder alerts, deepface auth checks
- BROWSER: Autonomous playwright tasks, fill form on website, google query, download file
- PLANNER: Complex multi-step instructions (e.g. build a website, build portfolio, generate script and test it)
- RAG: Read notes, search documents, summarize PDF, search PDF/DOCX
- CHAT: General conversational inquiries, greetings, simple questions

Output ONLY the category name. No explanations.

Command: {command}
"""
        category, model = route_llm(classification_prompt, task_type="general")
        category = category.strip().upper()
        
        speak_func(f"Brain classified query as {category} using {model}.")
        
        # 1. Planner routing
        if "PLANNER" in category:
            return self.planner.execute_autonomous_goal(command, speak_func=speak_func)
            
        # 2. Memory routing
        elif "MEMORY" in category:
            if "remember" in command.lower():
                # Extract fact
                fact = command.lower().replace("remember", "").strip()
                return self.memory_agent.handle_remember(fact)
            elif "recall" in command.lower():
                fact = command.lower().replace("recall", "").strip()
                return self.memory_agent.handle_recall(fact)
            elif "forget" in command.lower():
                fact = command.lower().replace("forget", "").strip()
                return self.memory_agent.handle_forget(fact)
            else:
                return self.memory_agent.handle_summarize()
                
        # 3. Vision routing
        elif "VISION" in category:
            if "screen" in command.lower() or "what is on my" in command.lower():
                return self.vision_agent.read_screen(command)
            elif "error" in command.lower() or "traceback" in command.lower():
                return self.vision_agent.explain_error()
            elif "holding" in command.lower() or "look at me" in command.lower():
                return self.vision_agent.analyze_webcam_feed(command)
            elif "who" in command.lower() or "person" in command.lower():
                return self.vision_agent.recognize_person()
            else:
                # Check for image file path in command
                import re
                path_match = re.search(r"(\b[a-zA-Z]:\\[^:\n\r\t]+|\b/[^:\n\r\t]+)", command)
                if path_match:
                    return self.vision_agent.analyze_local_image(path_match.group(0), command)
                return self.vision_agent.read_screen(command)

        # 4. Coding routing
        elif "CODING" in category:
            if "git" in command.lower():
                if "commit" in command.lower():
                    return self.coding_agent.git_auto_commit()
                # split git command arguments
                args = command.lower().replace("git", "").strip().split()
                return self.coding_agent.run_git_command(args)
            elif "review" in command.lower():
                file = command.split()[-1]
                return self.coding_agent.review_code(file)
            elif "fix" in command.lower() or "error" in command.lower():
                return "Sir, please provide the filename and error traceback to fix."
            else:
                # generate script name from command or default to auto_gen.py
                return self.coding_agent.write_code(command, "auto_gen.py")

        # 5. Research routing
        elif "RESEARCH" in category:
            if "http" in command.lower():
                import re
                url = re.search(r"(https?://\S+)", command).group(0)
                return self.research_agent.summarize_article(url)
            return self.research_agent.perform_search(command)

        # 6. Automation routing
        elif "AUTOMATION" in category:
            if "volume" in command.lower():
                action = "mute"
                if "up" in command.lower(): action = "up"
                elif "down" in command.lower(): action = "down"
                return self.automation_agent.control_volume(action)
            elif "open" in command.lower():
                app = command.lower().replace("open", "").strip()
                return self.automation_agent.open_app(app)
            elif "close" in command.lower():
                app = command.lower().replace("close", "").strip()
                return self.automation_agent.close_app(app)
            elif "shutdown" in command.lower():
                return self.automation_agent.shutdown_pc()
            elif "restart" in command.lower():
                return self.automation_agent.restart_pc()
            elif "sleep" in command.lower():
                return self.automation_agent.sleep_pc()
            else:
                return "Sir, I classified this as automation but could not resolve a target command."

        # 7. Security routing
        elif "SECURITY" in category:
            if "lock" in command.lower():
                return self.security_agent.lock_workstation()
            elif "intruder" in command.lower():
                return self.security_agent.trigger_intruder_detection()
            else:
                return self.security_agent.get_security_status()

        # 8. Browser routing
        elif "BROWSER" in category:
            if "search" in command.lower() or "google" in command.lower():
                q = command.lower().replace("search", "").replace("google", "").strip()
                return self.browser_agent.execute_quick_search(q)
            return self.browser_agent.run_autonomous_task(command)

        # 9. RAG routing
        elif "RAG" in category:
            if "index" in command.lower() or "scan" in command.lower():
                # Extract path
                import re
                path_match = re.search(r"(\b[a-zA-Z]:\\[^:\n\r\t]+|\b/[^:\n\r\t]+)", command)
                if path_match:
                    res = self.rag_engine.scan_and_index_directory(path_match.group(0))
                    return f"Index status: {res}"
                # scan current user folder
                from pathlib import Path
                res = self.rag_engine.scan_and_index_directory(str(Path.home() / "Documents"))
                return f"Scanning user Documents: {res}"
            ans, model = self.rag_engine.answer_query(command)
            return f"[Model: {model}]\n{ans}"

        # 10. General Chat conversation fallback
        else:
            prompt = f"""
You are JARVIS. Speak briefly, professionally, and call the user sir.
User asked: {command}
"""
            ans, model = route_llm(prompt, task_type="general")
            return f"[Model: {model}]\n{ans}"
