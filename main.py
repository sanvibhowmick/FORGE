import os
from typing import Literal
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
load_dotenv()

# Import our custom schema and utilities
from schema import ForgeState
from utils.workspace import initialize_workspace, list_workspace_tree
from utils.memory import init_memory, ingest_directory
from utils.judge import run_docker_judge

# Import our Agents
from agents.architect import architect_node
from agents.sqa import sqa_node
from agents.developer import lead_dev_node
from agents.auditor import auditor_node

# Load environment variables (OPENAI_API_KEY, QDRANT_URL)
load_dotenv()

# --- 1. THE ROUTING LOGIC ---
def judge_router(state: ForgeState) -> Literal["lead_dev", "auditor", "end"]:
    """
    Determines the next step based on the Docker Judge logs.
    """
    last_log = state.logs[-1] if state.logs else ""
    
    if "FAIL" in last_log:
        print("--- ROUTER: Tests failed. Sending back to Lead Dev for refactoring. ---")
        return "lead_dev"
    
    # If passed, we check if we've been hardened by the Auditor yet
    # We limit iterations to prevent infinite loops/cost
    if state.iteration < 3: 
        print("--- ROUTER: Initial tests passed. Sending to Auditor for hardening. ---")
        return "auditor"
    
    print("--- ROUTER: Project is hardened and complete. ---")
    return "end"

# --- 2. THE JUDGE NODE ---
def judge_node(state: ForgeState):
    """
    A simple wrapper to connect our Docker Utility to the Graph.
    """
    # Pull dependencies from the Architect's spec
    deps = state.spec.setup_commands if state.spec else []
    
    status, logs = run_docker_judge(dependencies=deps)
    state.logs.append(f"STATUS: {status}\n{logs}")
    return state

# --- 3. BUILDING THE GRAPH ---
workflow = StateGraph(ForgeState)

# Add all our specialized agents as nodes
workflow.add_node("architect", architect_node)
workflow.add_node("sqa_blind", sqa_node)
workflow.add_node("lead_dev", lead_dev_node)
workflow.add_node("judge", judge_node)
workflow.add_node("auditor", auditor_node)

# Define the flow
workflow.set_entry_point("architect")
workflow.add_edge("architect", "sqa_blind")
workflow.add_edge("sqa_blind", "lead_dev")
workflow.add_edge("lead_dev", "judge")

# Conditional Routing: Does the code pass?
workflow.add_conditional_edges(
    "judge",
    judge_router,
    {
        "lead_dev": "lead_dev", # Fix bugs
        "auditor": "auditor",   # Try to break it
        "end": END              # Finish
    }
)

# After Auditor adds new tests, it goes back to Lead Dev to pass them
workflow.add_edge("auditor", "lead_dev")

# Compile the graph
app = workflow.compile()

# --- 4. EXECUTION ---
if __name__ == "__main__":
    # A. Setup the environment
    initialize_workspace()
    init_memory()
    
    # B. OPTIONAL: Ingest existing files if you're in a 'Brownfield' project
    # ingest_directory("./existing_code") 

    # C. Start the Factory
    user_input = input("What would you like FORGE to build today? ")
    
    initial_state = {
        "requirement": user_input,
        "iteration": 0,
        "logs": []
    }
    
    print("\n🚀 FORGE is spinning up the engineering pipeline...\n")
    for output in app.stream(initial_state):
        # This allows you to see the state transitions in your terminal
        for node_name, state_update in output.items():
            print(f"✔️ Node '{node_name}' completed execution.")
    
    print("\n✅ Project Complete! Check your './workspace' directory.")
    print(list_workspace_tree())