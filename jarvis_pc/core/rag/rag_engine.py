import os
import glob
from pathlib import Path
from docx import Document
from pypdf import PdfReader
from core.memory.vector_db import VectorMemory
from core.router.llm_router import route_llm

class RAGEngine:
    def __init__(self, db_path="jarvis_memory.db"):
        self.vector_db = VectorMemory(db_path=db_path)

    def extract_text_from_pdf(self, file_path: str) -> str:
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
            return text
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
            return ""

    def extract_text_from_docx(self, file_path: str) -> str:
        try:
            doc = Document(file_path)
            text = []
            for para in doc.paragraphs:
                text.append(para.text)
            return "\n".join(text)
        except Exception as e:
            print(f"Error reading DOCX {file_path}: {e}")
            return ""

    def extract_text_from_txt(self, file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading TXT {file_path}: {e}")
            return ""

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks

    def index_file(self, file_path: str) -> int:
        """Parses a file, splits it into chunks, and saves it to Vector Memory."""
        p = Path(file_path)
        ext = p.suffix.lower()
        text = ""

        if ext == ".pdf":
            text = self.extract_text_from_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            text = self.extract_text_from_docx(file_path)
        elif ext in [".txt", ".md", ".py", ".js", ".html", ".css", ".json"]:
            text = self.extract_text_from_txt(file_path)

        if not text.strip():
            return 0

        chunks = self.chunk_text(text)
        for i, chunk in enumerate(chunks):
            metadata = {
                "source": file_path,
                "filename": p.name,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            self.vector_db.remember(chunk, metadata)
            
        return len(chunks)

    def scan_and_index_directory(self, directory_path: str) -> dict:
        """Scans a directory for supported files and indexes them."""
        supported_extensions = ["*.pdf", "*.docx", "*.txt", "*.md", "*.py"]
        indexed_stats = {}
        
        path = Path(directory_path)
        if not path.exists():
            return {"error": f"Directory {directory_path} does not exist."}

        files_indexed = 0
        chunks_indexed = 0
        
        for ext in supported_extensions:
            # Recursive search
            for filepath in glob.glob(os.path.join(directory_path, "**", ext), recursive=True):
                try:
                    num_chunks = self.index_file(filepath)
                    if num_chunks > 0:
                        files_indexed += 1
                        chunks_indexed += num_chunks
                        indexed_stats[Path(filepath).name] = num_chunks
                except Exception as e:
                    print(f"Error indexing {filepath}: {e}")

        return {
            "status": "success",
            "files_indexed": files_indexed,
            "chunks_indexed": chunks_indexed,
            "details": indexed_stats
        }

    def answer_query(self, query: str) -> tuple[str, str]:
        """Queries the vector database for RAG context and answers the user query."""
        recalled = self.vector_db.recall(query, limit=5)
        if not recalled or recalled[0]["score"] < 0.2:
            return "Sir, I could not find any relevant local context or documents for that query.", "N/A"

        context_blocks = []
        sources = set()
        for item in recalled:
            context_blocks.append(f"Source: {item['metadata'].get('filename', 'Unknown')}\nContent: {item['text']}")
            sources.add(item['metadata'].get('filename', 'Unknown'))

        context_str = "\n\n---\n\n".join(context_blocks)
        
        prompt = f"""
You are JARVIS. Answer the user's question using ONLY the provided local document context. If the answer cannot be found in the context, say that the information was not found in local files.

Document Context:
{context_str}

User Question: {query}
"""
        response, model = route_llm(prompt, task_type="research")
        sources_str = ", ".join(sources)
        return f"{response}\n\n[Sources: {sources_str}]", model
