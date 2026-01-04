import os
from openai import OpenAI
from schema import TechnicalSpec, ForgeState
from utils.memory import get_context
from utils.workspace import write_to_path

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def architect_node(state: ForgeState):
    print("--- ARCHITECT (GPT-5 Mini): Designing Multi-File Architecture ---")
    
    # 1. Retrieve the "Essence" of the existing codebase from Qdrant
    state.context_from_db = get_context(state.requirement)
    
    prompt = f"""
    You are the Lead Architect at FORGE, an automated AI Engineering Firm.
    
    EXISTING REPOSITORY CONTEXT:
    {state.context_from_db if state.context_from_db else "No existing files. Starting a new repository."}
    
    NEW PROJECT REQUIREMENT:
    {state.requirement}
    
    TASK:
    Generate a Technical Specification in JSON format for a multi-file project.
    
    REQUIREMENTS:
   You must output a TechnicalSpec.
1. file_structure: List every file needed (src/..., tests/..., README.md).
2. functions: Detail the core logic functions.
3. setup_commands: List shell commands to prepare the environment.
    4. Ensure compatibility with existing files found in the context.
    """

    # 2. Use Structured Outputs to ensure the Lead Dev gets a perfect JSON map
    response = client.beta.chat.completions.parse(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "You are a senior system architect. You design modular, scalable repository structures."},
            {"role": "user", "content": prompt}
        ],
        response_format=TechnicalSpec,
    )

    state.spec = response.choices[0].message.parsed
    
    # 3. PHYSICAL ACTION: Write the blueprint to the workspace for the user/IDE
    write_to_path("spec.json", state.spec.model_dump_json(indent=2))
    
    print(f"--- ARCHITECT: Blueprint for '{state.spec.project_name}' saved to workspace ---")
    return state