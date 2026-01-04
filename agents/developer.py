import os
from openai import OpenAI
from schema import ForgeState
from utils.workspace import write_to_path, run_command

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def lead_dev_node(state: ForgeState):
    print(f"--- LEAD DEV (GPT-5 Mini): Building/Refactoring Iteration {state.iteration} ---")
    
    # 1. Setup Phase: Run commands (only on the first try)
    if state.iteration == 0:
        print("--- LEAD DEV: Running initial setup commands ---")
        for cmd in state.spec.setup_commands:
            run_command(cmd)

    # 2. Logic Phase: Decide which files to write/fix
    # If we have failure logs, we focus on the specific files mentioned in the traceback
    feedback = state.logs[-1] if state.logs else "Initial build phase."
    
    for file_plan in state.spec.file_structure:
        print(f"--- LEAD DEV: Working on {file_plan.path} ---")
        
        prompt = f"""
        You are the Lead Developer at FORGE. 
        You are building a multi-file project based on this Architect's Spec.
        
        FILE TO WRITE: {file_plan.path}
        FILE DESCRIPTION: {file_plan.description}
        
        CURRENT FEEDBACK/ERRORS:
        {feedback}
        
        GOAL:
        Write the code for this specific file. Ensure it integrates with the rest 
        of the repository. If there are Auditor exploit tests failing in the logs, 
        you MUST refactor this file to handle those edge cases.
        
        OUTPUT ONLY THE RAW CODE.
        """

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are a world-class Python engineer. You build resilient, multi-file systems."},
                {"role": "user", "content": prompt}
            ]
        )

        # 3. PHYSICAL ACTION: Write each file to its path in your IDE
        write_to_path(file_plan.path, response.choices[0].message.content)

    state.iteration += 1
    print(f"--- LEAD DEV: Workspace updated for iteration {state.iteration} ---")
    return state