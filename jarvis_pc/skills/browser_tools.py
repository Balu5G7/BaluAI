import os
import json
import time
import base64
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

LOG_PATH = Path("logs/browser_logs.json")

class BrowserTools:
    def __init__(self, headless=False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self._init_logs()

    def _init_logs(self):
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not LOG_PATH.exists():
            with open(LOG_PATH, "w", encoding="utf-8") as f:
                json.dump([], f)

    def log_action(self, url: str, action: str, success: bool, details: str = ""):
        try:
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []
            
        logs.append({
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "action": action,
            "success": success,
            "details": details
        })
        
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=4)

    def is_safe_action(self, text: str) -> bool:
        """Security: blocks sensitive actions without user confirmation."""
        blocklist = ["buy", "purchase", "pay", "checkout", "transfer money", "delete account", "deactivate"]
        text_lower = text.lower()
        for word in blocklist:
            if word in text_lower:
                return False
        return True

    def start(self):
        if not self.playwright:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            self.context = self.browser.new_context()
            self.page = self.context.new_page()

    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.playwright = None

    def goto(self, url: str) -> str:
        if not url.startswith("http"):
            url = "https://" + url
        try:
            self.page.goto(url, wait_until="domcontentloaded", timeout=15000)
            self.log_action(url, "GOTO", True)
            return f"Successfully navigated to {url}"
        except Exception as e:
            self.log_action(url, "GOTO", False, str(e))
            return f"Error navigating: {e}"

    def extract_dom(self):
        """Returns a list of interactive elements on the page."""
        try:
            self.page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass # Ignore timeout if network isn't fully idle
            
        elements_info = []
        try:
            # Extract links
            links = self.page.query_selector_all("a")
            for i, link in enumerate(links[:40]):
                text = (link.inner_text() or "").strip()
                if text:
                    elements_info.append(f"[LINK] idx={i} text='{text}'")

            # Extract inputs
            inputs = self.page.query_selector_all("input, textarea")
            for i, inp in enumerate(inputs[:30]):
                name = inp.get_attribute("name") or ""
                ph = inp.get_attribute("placeholder") or ""
                elements_info.append(f"[INPUT] idx={i} name='{name}' placeholder='{ph}'")

            # Extract buttons
            buttons = self.page.query_selector_all("button, input[type='submit']")
            for i, btn in enumerate(buttons[:30]):
                text = (btn.inner_text() or btn.get_attribute("value") or "").strip()
                if text:
                    elements_info.append(f"[BUTTON] idx={i} text='{text}'")
                    
        except Exception as e:
            return f"Error extracting DOM: {e}"
            
        return "\n".join(elements_info)

    def click_element(self, elem_type: str, idx: int) -> str:
        """Clicks an element from the extracted lists."""
        try:
            if elem_type == "LINK":
                elems = self.page.query_selector_all("a")
            elif elem_type == "INPUT":
                elems = self.page.query_selector_all("input, textarea")
            elif elem_type == "BUTTON":
                elems = self.page.query_selector_all("button, input[type='submit']")
            else:
                return "Unknown element type."

            if idx >= len(elems):
                return f"Error: Index {idx} out of bounds."
                
            elem = elems[idx]
            text = elem.inner_text() or elem.get_attribute("value") or ""
            
            if not self.is_safe_action(text):
                self.log_action(self.page.url, f"CLICK BLOCKED", False, text)
                return f"Security blocked clicking on: '{text}'. Operation aborted."
                
            elem.click()
            self.log_action(self.page.url, f"CLICK {elem_type} {idx}", True, text)
            return f"Successfully clicked {elem_type} '{text}'"
        except Exception as e:
            self.log_action(self.page.url, f"CLICK {elem_type} {idx}", False, str(e))
            return f"Error clicking element: {e}"

    def type_text(self, idx: int, text: str) -> str:
        try:
            inputs = self.page.query_selector_all("input, textarea")
            if idx >= len(inputs):
                return f"Error: Input index {idx} out of bounds."
            
            inputs[idx].fill(text)
            self.log_action(self.page.url, f"TYPE {idx}", True, "Text typed successfully.")
            return f"Successfully typed into input {idx}."
        except Exception as e:
            self.log_action(self.page.url, f"TYPE {idx}", False, str(e))
            return f"Error typing text: {e}"

    def take_screenshot(self) -> str:
        """Takes a screenshot and returns the file path for Gemini Vision."""
        try:
            path = str(Path("logs/screenshot.jpg").absolute())
            self.page.screenshot(path=path, full_page=False)
            return path
        except Exception as e:
            return ""
