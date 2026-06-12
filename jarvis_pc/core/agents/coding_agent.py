import os
import re
import subprocess
from pathlib import Path
from core.router.llm_router import route_llm

class CodingAgent:
    def __init__(self, workspace_path=None):
        if not workspace_path:
            self.workspace_path = Path.home() / "JARVIS_Projects"
        else:
            self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(exist_ok=True)

    def write_code(self, prompt: str, filename: str) -> str:
        """Generates code using Claude and saves it to a file."""
        code_prompt = f"""
Goal: Write code for {filename}
Requirement: {prompt}

Write the complete code. Output ONLY the file content inside a markdown block. No explanations.
"""
        response, model = route_llm(code_prompt, task_type="coding")
        
        # Extract content inside markdown
        match = re.search(r"```[a-zA-Z]*\n(.*?)\n```", response, re.DOTALL)
        code = match.group(1).strip() if match else response.strip()
        
        file_path = self.workspace_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
            
        return f"Sir, I have written the code using {model} and saved it to {file_path}."

    def review_code(self, filename: str) -> str:
        """Reads a file and reviews the code for bugs, style, and optimizations."""
        file_path = self.workspace_path / filename
        if not file_path.exists():
            # Check local directory
            file_path = Path(filename)
            if not file_path.exists():
                return f"Sir, I could not locate the file {filename}."

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        prompt = f"""
Analyze the following code for bugs, syntax errors, style issues, and security vulnerabilities.
Provide recommendations for optimization.

File: {file_path.name}
Code:
{content}
"""
        response, model = route_llm(prompt, task_type="coding")
        return f"[Reviewed with {model}]\n{response}"

    def fix_bugs(self, filename: str, error_message: str) -> str:
        """Fixes code based on an error message."""
        file_path = self.workspace_path / filename
        if not file_path.exists():
            file_path = Path(filename)
            if not file_path.exists():
                return f"Sir, I could not find the file {filename} to fix."

        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        prompt = f"""
We ran the code in {file_path.name} and got this error:
{error_message}

Current Code:
{code}

Please fix the code. Output ONLY the corrected complete code inside a ``` python code block.
"""
        fixed_code, model = route_llm(prompt, task_type="coding")
        
        match = re.search(r"```[a-zA-Z]*\n(.*?)\n```", fixed_code, re.DOTALL)
        code = match.group(1).strip() if match else fixed_code.strip()
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        return f"Sir, I corrected the file {file_path.name} using {model} based on the error output."

    def run_git_command(self, git_args: list[str]) -> str:
        """Automates git commands in the current workspace."""
        try:
            # First find if git is initialized in the workspace or parent workspace
            cmd = ["git"] + git_args
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=str(os.getcwd()),  # Run in active repository
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=15
            )
            output = result.stdout or result.stderr
            return f"Git output:\n{output}"
        except Exception as e:
            return f"Error executing git command: {e}"

    def git_auto_commit(self, commit_msg: str = "JARVIS auto-update") -> str:
        """Automates Git stages, commits, and pushes current changes."""
        add_res = self.run_git_command(["add", "."])
        commit_res = self.run_git_command(["commit", "-m", commit_msg])
        push_res = self.run_git_command(["push"])
        return f"Git automation complete, sir.\n{add_res}\n{commit_res}\n{push_res}"
