import os
import shutil
from pathlib import Path

def create_file(filepath: str, content: str = "") -> str:
    try:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Created file: {filepath}"
    except Exception as e:
        return f"Error creating {filepath}: {e}"

def read_file(filepath: str) -> str:
    try:
        return Path(filepath).read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file: {e}"

def delete_file(filepath: str) -> str:
    try:
        os.remove(filepath)
        return f"Deleted: {filepath}"
    except Exception as e:
        return f"Error deleting: {e}"

def move_file(source: str, destination: str) -> str:
    try:
        shutil.move(source, destination)
        return f"Moved {source} to {destination}"
    except Exception as e:
        return f"Error moving file: {e}"

def list_directory(dirpath: str) -> str:
    try:
        items = list(Path(dirpath).iterdir())
        return "\n".join(str(i) for i in items)
    except Exception as e:
        return f"Error listing directory: {e}"

def create_folder(folder_path: str) -> str:
    try:
        os.makedirs(folder_path, exist_ok=True)
        return f"Folder created: {folder_path}"
    except Exception as e:
        return f"Error creating folder: {e}"

def read_pdf(filepath: str) -> str:
    try:
        import pypdf
        reader = pypdf.PdfReader(filepath)
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        return text.strip() if text else "This PDF contains no extractable text."
    except Exception as e:
        return f"Error reading PDF: {e}"

