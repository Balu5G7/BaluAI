import os
import sqlite3
import json
import numpy as np
from google import genai

class VectorMemory:
    def __init__(self, db_path="jarvis_memory.db"):
        self.db_path = db_path
        self._init_db()
        
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn
        
    def _init_db(self):
        conn = self._connect()
        cursor = conn.cursor()
        
        # Memory storage: text, metadata (JSON), embedding vector (binary BLOB)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                metadata TEXT,
                embedding BLOB NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def _get_embedding(self, text: str) -> list[float]:
        """Fetch embedding vector from Gemini API."""
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            # Fallback mock embedding if key is missing
            return [0.0] * 768
            
        try:
            client = genai.Client(api_key=api_key)
            result = client.models.embed_content(
                model="text-embedding-004",
                contents=text
            )
            # Fetch the embedding values
            return result.embeddings[0].values
        except Exception as e:
            print("Embedding API Error:", e)
            return [0.0] * 768

    def remember(self, text: str, metadata: dict = None) -> int:
        """Stores a new fact/memory along with its embedding."""
        embedding = self._get_embedding(text)
        embedding_blob = np.array(embedding, dtype=np.float32).tobytes()
        
        meta_str = json.dumps(metadata or {})
        
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO memories (text, metadata, embedding) VALUES (?, ?, ?)",
            (text, meta_str, embedding_blob)
        )
        mem_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return mem_id

    def recall(self, query: str, limit: int = 5) -> list[dict]:
        """Performs cosine-similarity search against stored memories."""
        query_vector = np.array(self._get_embedding(query), dtype=np.float32)
        
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, text, metadata, embedding, timestamp FROM memories")
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            mem_id, text, meta_str, emb_blob, timestamp = row
            
            # Reconstruct vector from blob
            emb_vector = np.frombuffer(emb_blob, dtype=np.float32)
            
            # Calculate Cosine Similarity
            dot_product = np.dot(query_vector, emb_vector)
            norm_q = np.linalg.norm(query_vector)
            norm_e = np.linalg.norm(emb_vector)
            
            similarity = 0.0
            if norm_q > 0 and norm_e > 0:
                similarity = float(dot_product / (norm_q * norm_e))
                
            results.append({
                "id": mem_id,
                "text": text,
                "metadata": json.loads(meta_str),
                "timestamp": timestamp,
                "score": similarity
            })
            
        # Sort by similarity score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def forget(self, memory_id: int) -> bool:
        """Deletes a memory by its ID."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        rows_deleted = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_deleted > 0

    def forget_by_text(self, text_query: str) -> int:
        """Deletes memories that closely match the text query."""
        recalled = self.recall(text_query, limit=3)
        deleted_count = 0
        for item in recalled:
            if item["score"] > 0.8: # strong match
                if self.forget(item["id"]):
                    deleted_count += 1
        return deleted_count

    def clear_all(self):
        """Clears all vector memories."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memories")
        conn.commit()
        conn.close()
        
    def summarize_memory(self) -> str:
        """Returns a string listing recent facts stored in memory."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT text FROM memories ORDER BY id DESC LIMIT 50")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return "No memories recorded, sir."
            
        summary = "Recent stored memories:\n"
        for i, row in enumerate(rows, 1):
            summary += f"{i}. {row[0]}\n"
        return summary
