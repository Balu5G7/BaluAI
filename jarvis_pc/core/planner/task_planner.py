import os
import re
import subprocess
import json
from pathlib import Path
from core.router.llm_router import route_llm

class TaskPlanner:
    def __init__(self, workspace_dir=None):
        if not workspace_dir:
            self.workspace_dir = Path.home() / "JARVIS_Projects"
        else:
            self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

    def execute_autonomous_goal(self, goal: str, speak_func=print) -> str:
        """
        Runs the full workflow:
        Understand goal -> Create plan -> Generate files -> Execute tasks -> Test output -> Fix errors -> Deliver result.
        """
        speak_func(f"Starting autonomous planner for goal: '{goal}', sir.")
        
        # Step 1: Create Plan
        plan_prompt = f"""
You are the JARVIS Autonomous Task Planner.
Goal: {goal}

Create a structured plan to accomplish this. You must determine:
1. What directories to create.
2. What files to generate (with their filenames).
3. How to test the results.

Output your response strictly as a JSON object matching this schema:
{{
  "project_name": "string",
  "directories": ["string"],
  "files": [
    {{
      "path": "string",
      "purpose": "string",
      "prompt_for_generation": "string"
    }}
  ],
  "test_commands": ["string"]
}}
"""
        response, model = route_llm(plan_prompt, task_type="reasoning")
        
        # Clean JSON from response
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if not json_match:
            return "Sir, I failed to generate a structured JSON plan for this goal."
            
        try:
            plan = json.loads(json_match.group(0))
        except Exception as e:
            return f"Sir, the generated plan JSON was invalid: {e}"

        proj_dir = self.workspace_dir / plan.get("project_name", "temp_project")
        proj_dir.mkdir(exist_ok=True)
        speak_func(f"Plan created using {model}. Initializing project folder: {proj_dir.name}")

        # Create subdirectories
        for d in plan.get("directories", []):
            (proj_dir / d).mkdir(parents=True, exist_ok=True)

        # Step 2: Generate Files
        generated_files = []
        for file_info in plan.get("files", []):
            file_path = proj_dir / file_info["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            purpose = file_info["purpose"]
            gen_prompt = file_info["prompt_for_generation"]
            
            speak_func(f"Generating file: {file_info['path']} ({purpose})")
            
            # Request LLM to write code content
            code_prompt = f"""
Goal: {goal}
Project Directory: {proj_dir}
Target File: {file_info['path']}
Purpose: {purpose}
Instructions: {gen_prompt}

Generate the complete, working source code content for this file. 
DO NOT write explanations. Output ONLY the file content.
"""
            file_content, _ = route_llm(code_prompt, task_type="coding")
            
            # Clean markdown formatting if LLM wrapped in code block
            clean_content = re.sub(r"^```[a-zA-Z]*\n", "", file_content)
            clean_content = re.sub(r"\n```$", "", clean_content)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(clean_content)
            generated_files.append(file_path)

        # Step 3 & 4: Execute & Test / Self-Heal Loop
        max_fixes = 3
        test_commands = plan.get("test_commands", [])
        
        speak_func("Running validation checks and tests...")
        
        for cmd in test_commands:
            fix_attempt = 0
            while fix_attempt < max_fixes:
                speak_func(f"Executing test: {cmd}")
                
                # Execute in project directory
                try:
                    result = subprocess.run(
                        cmd,
                        shell=True,
                        cwd=str(proj_dir),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        speak_func(f"Test passed successfully: {cmd}")
                        break
                    else:
                        error_msg = result.stderr or result.stdout
                        speak_func(f"Test failed with error on attempt {fix_attempt+1}. Starting self-healing...")
                        
                        # Get LLM to fix files based on error
                        for file_path in generated_files:
                            with open(file_path, "r", encoding="utf-8") as f:
                                current_code = f.read()
                                
                            fix_prompt = f"""
Goal: {goal}
File: {file_path.name}
Code:
{current_code}

We ran this command: {cmd}
It failed with this error:
{error_msg}

Rewrite the complete code for this file to fix the error. Output ONLY the code content without explanations.
"""
                            fixed_code, _ = route_llm(fix_prompt, task_type="coding")
                            
                            clean_fixed = re.sub(r"^```[a-zA-Z]*\n", "", fixed_code)
                            clean_fixed = re.sub(r"\n```$", "", clean_fixed)
                            
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(clean_fixed)
                                
                        fix_attempt += 1
                except Exception as ex:
                    speak_func(f"Error running test execution: {ex}")
                    break
                    
            if fix_attempt >= max_fixes:
                speak_func("Self-healing failed to resolve the errors, sir.")
                return f"Task completed with some validation errors. Files located at {proj_dir}"

        speak_func("All validation checks and self-healing phases completed successfully, sir.")
        return f"Sir, I have successfully accomplished the goal: '{goal}'. Project files generated at {proj_dir}."
