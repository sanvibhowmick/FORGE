import os
import subprocess
import shutil
from pathlib import Path

# The absolute path to your IDE workspace
WORKSPACE_DIR = os.path.abspath("./workspace")

def initialize_workspace():
    """Wipes the workspace and starts fresh for a new project."""
    if os.path.exists(WORKSPACE_DIR):
        shutil.rmtree(WORKSPACE_DIR)
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    print(f"--- WORKSPACE: Initialized at {WORKSPACE_DIR} ---")

def write_to_path(relative_path: str, content: str):
    """
    Writes content to a specific file path. 
    If the folders don't exist (e.g., 'src/auth/'), it creates them.
    """
    full_path = os.path.join(WORKSPACE_DIR, relative_path)
    
    # Create parent directories automatically
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    return relative_path

def run_command(command: str):
    """
    Executes a shell command (pip, pytest, etc.) inside the workspace.
    Returns the output (stdout + stderr) for the agents to read.
    """
    print(f"--- COMMANDER: Running '$ {command}' ---")
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=WORKSPACE_DIR,
            capture_output=True,
            text=True,
            timeout=60 # Safety timeout for long-running builds
        )
        # Combine output so the Lead Dev can see exactly what happened
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "ERROR: Command timed out after 60 seconds."
    except Exception as e:
        return f"ERROR: {str(e)}"

def list_workspace_tree():
    """Returns a visual tree of the files currently in your IDE workspace."""
    tree = []
    for root, dirs, files in os.walk(WORKSPACE_DIR):
        level = root.replace(WORKSPACE_DIR, '').count(os.sep)
        indent = ' ' * 4 * (level)
        tree.append(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            tree.append(f"{subindent}{f}")
    return "\n".join(tree)