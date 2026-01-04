import os
from openai import OpenAI
from schema import ForgeState
from utils.workspace import write_to_path

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def sqa_node(state: ForgeState):
    print("--- BLIND SQA (GPT-5 Mini): Architecting Test Suite ---")
    
    # We provide the full Multi-File Spec to the SQA
    spec_json = state.spec.model_dump_json(indent=2)
    
    prompt = f"""
    You are the Senior QA Engineer. You are 'Blind' to the Lead Dev's implementation.
    Your task is to create a complete Pytest suite for the following architecture.
    
    TECHNICAL SPECIFICATION:
    {spec_json}
    
    TASK:
    1. Identify the core logic files that need testing.
    2. Write high-coverage Pytest code for each component.
    3. Ensure tests account for the directory structure (e.g., 'from src.auth import login').
    4. Mock external services or databases if mentioned in the spec.
    
    OUTPUT FORMAT:
    Return a list of files to be created in the following format:
    FILE: tests/test_auth.py
    ```python
    (code here)
    ```
    FILE: tests/test_utils.py
    ```python
    (code here)
    ```
    """

    # Using GPT-5 Mini to handle the structural logic
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "You are a specialized QA automation agent. Output file paths and pure Python code."},
            {"role": "user", "content": prompt}
        ]
    )

    raw_output = response.choices[0].message.content
    state.test_code = raw_output # Storing raw output for the Lead Dev to see later

    # PHYSICAL ACTION: Parse the output and write the files to the workspace
    # Simple parser to split the files based on the "FILE:" marker
    parts = raw_output.split("FILE: ")
    for part in parts:
        if part.strip():
            lines = part.strip().split("\n")
            file_path = lines[0].strip()
            # Extract code between ```python and ```
            code_content = part.split("```python")[1].split("```")[0].strip()
            write_to_path(file_path, code_content)
            print(f"--- SQA: Saved test file to {file_path} ---")

    return state