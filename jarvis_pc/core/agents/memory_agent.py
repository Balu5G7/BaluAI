from core.memory.vector_db import VectorMemory
from core.memory import MemoryDB

class MemoryAgent:
    def __init__(self, db_path="jarvis_memory.db", chat_db_path="jarvis.db"):
        self.vector_db = VectorMemory(db_path=db_path)
        self.chat_db = MemoryDB(db_path=chat_db_path)

    def handle_remember(self, text: str, metadata: dict = None) -> str:
        """Stores a fact into the vector semantic memory."""
        mem_id = self.vector_db.remember(text, metadata)
        return f"Sir, I have stored that in my long-term memory: '{text}' (ID: {mem_id})."

    def handle_recall(self, query: str) -> str:
        """Recalls facts related to the query."""
        results = self.vector_db.recall(query, limit=3)
        if not results or results[0]["score"] < 0.2:
            return "Sir, I do not recall anything relevant to that in my long-term memory."
            
        facts = []
        for i, item in enumerate(results, 1):
            facts.append(f"{i}. {item['text']} (relevance: {int(item['score']*100)}%)")
        return "Here is what I recalled from memory, sir:\n" + "\n".join(facts)

    def handle_forget(self, text_query: str) -> str:
        """Forgets facts related to the query."""
        deleted = self.vector_db.forget_by_text(text_query)
        if deleted > 0:
            return f"Sir, I have forgotten {deleted} matching memories from my database."
        return "I could not find any memories close enough to that description to forget, sir."

    def handle_summarize(self) -> str:
        """Summarizes all stored facts."""
        return self.vector_db.summarize_memory()
