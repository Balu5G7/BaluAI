from core.planner.browser_planner import BrowserPlanner

class BrowserAgent:
    def __init__(self, headless=False):
        self.headless = headless

    def execute_quick_search(self, query: str) -> str:
        """Legacy fallback to maintain command compatibility, now routes through autonomous execution."""
        return self.run_autonomous_task(f"Search Google for {query} and summarize the top 3 results.")

    def run_autonomous_task(self, goal: str, speak_func=print) -> str:
        """
        Runs the fully autonomous, production-grade Playwright browsing loop.
        Integrates IPC GUI animations, security blocklists, and Gemini Vision fallback.
        """
        planner = BrowserPlanner(headless=self.headless)
        return planner.execute_goal(goal, speak_func)
