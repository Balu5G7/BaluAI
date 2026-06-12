import urllib.request
import urllib.parse
import json
import re
from core.router.llm_router import route_llm

class ResearchAgent:
    def __init__(self):
        pass

    def perform_search(self, query: str) -> str:
        """Searches Wikipedia or Google and compiles results."""
        # Simple wikipedia API lookup as a robust, non-blocked way to research
        try:
            encoded_query = urllib.parse.quote(query)
            wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded_query}&format=json"
            
            req = urllib.request.Request(
                wiki_url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
            search_results = data.get("query", {}).get("search", [])
            if not search_results:
                return f"Sir, no Wikipedia entries found for '{query}'."
                
            compiled = []
            for item in search_results[:4]:
                title = item.get("title")
                snippet = item.get("snippet")
                # Remove html tags
                clean_snippet = re.sub(r'<[^>]*>', '', snippet)
                compiled.append(f"Topic: {title}\nSnippet: {clean_snippet}\n")
                
            research_context = "\n".join(compiled)
            
            # Use Gemini to summarize the compiled research
            prompt = f"""
You are JARVIS. Below is a compiled snippet from Wikipedia search on '{query}':
{research_context}

Write a comprehensive, professional, and clear executive summary answering the user query: '{query}'.
"""
            response, model = route_llm(prompt, task_type="research")
            return f"[Research source: Wikipedia | Compiled using {model}]\n{response}"
            
        except Exception as e:
            return f"Sir, I ran into an issue while researching: {e}"

    def summarize_article(self, url: str) -> str:
        """Reads a webpage article and summarizes it."""
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8', errors='ignore')
                
            # Remove scripts, styles
            text = re.sub(r'<(script|style).*?>.*?</\1>', '', html, flags=re.DOTALL)
            # Remove all tags
            text = re.sub(r'<.*?>', '', text)
            # Collapse whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Slice text to keep within reasonable limits (e.g. 8000 characters)
            text_snippet = text[:8000]
            
            prompt = f"""
You are JARVIS. Summarize the content of the article from {url}:

Content:
{text_snippet}
"""
            response, model = route_llm(prompt, task_type="research")
            return f"[Summarized from {url} using {model}]\n{response}"
        except Exception as e:
            return f"Sir, I failed to scrape the article at {url}. Error: {e}"
