# JARVIS Memory Package
# Re-export MemoryDB so existing imports like `from core.memory import MemoryDB` continue to work.

import sqlite3


class MemoryDB:
    def __init__(self, db_path="jarvis.db"):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=5)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self):
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    # -------------------------
    # Conversation History
    # -------------------------

    def add_message(self, role, content):
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO conversation_history (role, content) VALUES (?, ?)",
            (role, content)
        )

        conn.commit()
        conn.close()

    def get_history(self, limit=20):
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT role, content FROM conversation_history ORDER BY id DESC LIMIT ?",
            (limit,)
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {"role": row[0], "content": row[1]}
            for row in reversed(rows)
        ]

    def clear_history(self):
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM conversation_history")

        conn.commit()
        conn.close()

    # -------------------------
    # Permanent Memory
    # -------------------------

    def remember_fact(self, key, value):
        self.add_message("memory", f"{key}:{value}")

    def recall_fact(self, key):
        history = self.get_history(500)

        for item in reversed(history):
            if item["role"] == "memory":
                try:
                    k, v = item["content"].split(":", 1)
                    if k.lower().strip() == key.lower().strip():
                        return v
                except Exception:
                    pass

        return None

    def list_memories(self):
        history = self.get_history(500)

        memories = []

        for item in history:
            if item["role"] == "memory":
                memories.append(item["content"])

        return memories
