import os
from openai import OpenAI
from schema import ForgeState
from utils.workspace import write_to_path

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def auditor_node(state: ForgeState):
    print("--- THE AUDITOR (GPT-5 Mini): Identifying High-Risk Targets ---")

    # 1. First Pass: Select targets based on the File Structure (Cost: Minimal)
    file_list = [f.path for f in state.spec.file_structure]
    
    selection_prompt = f"""
    You are a Security Auditor. You have a limited token budget.
    Identify the top 2-3 files from this list that are most critical to system logic or security.
    
    PROJECT SPEC: {state.spec.project_name}
    FILE LIST: {", ".join(file_list)}
    
    Return ONLY a comma-separated list of paths.
    """

    selection_response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": selection_prompt}]
    )
    
    target_paths = [path.strip() for path in selection_response.choices[0].message.content.split(",")]

    # 2. Second Pass: Deep Audit of targeted files
    selected_content = []
    for path in target_paths:
        full_path = os.path.join("./workspace", path)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                selected_content.append(f"FILE: {path}\nCONTENT:\n{f.read()}")

    print(f"--- THE AUDITOR: Auditing {', '.join(target_paths)} ---")

    audit_prompt = f"""
    You are the Senior Security Auditor. 
    The Lead Dev has passed initial tests. You must now find subtle logic holes or security flaws.
    
    TARGETED CODE:
    {"\n\n---\n\n".join(selected_content)}
    
    TASK:
    1. Identify 2 'Hidden' edge cases or vulnerabilities.
    2. Write ADVANCED Pytest functions that will FAIL the current implementation.
    
    OUTPUT FORMAT:
    TARGET_FILE: tests/test_security_audit.py
    ```python
    (exploit code here)
    ```
    """

    audit_response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "You are an adversarial auditor. Your goal is to break the code."},
            {"role": "user", "content": audit_prompt}
        ]
    )

    # 3. PHYSICAL ACTION: Append the new "Vulnerability Tests" to the workspace
    raw_audit = audit_response.choices[0].message.content
    if "TARGET_FILE:" in raw_audit:
        parts = raw_audit.split("TARGET_FILE: ")
        for part in parts[1:]:
            lines = part.strip().split("\n")
            target_test_file = lines[0].strip()
            exploit_code = part.split("```python")[1].split("```")[0].strip()
            
            # Write to a new audit-specific test file to keep things clean
            write_to_path(target_test_file, exploit_code)
            print(f"--- AUDITOR: Hardened {target_test_file} with new exploit cases ---")

    return state