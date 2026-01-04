import docker
import os

def run_docker_judge(dependencies: list = None):
    """Impartial referee: Runs the entire test suite in an isolated Docker sandbox."""
    client = docker.from_env()
    abs_workspace_path = os.path.abspath("./workspace")
    
    # 1. CLEAN DEPENDENCIES: Only take the package names, ignore complex shell logic
    # We filter out things like 'git', 'venv', 'source' which shouldn't run in Docker
    safe_deps = []
    if dependencies:
        for d in dependencies:
            if any(forbidden in d.lower() for forbidden in ["venv", "source", "git", "cd "]):
                continue
            safe_deps.append(d)
    
    if "pytest" not in safe_deps:
        safe_deps.append("pytest")
    
    # Simple chain: install what is needed, then run the tests
    install_cmd = f"pip install {' '.join(safe_deps)}"
    full_cmd = f"bash -c '{install_cmd} && pytest /app/tests --tb=short'"
    
    print(f"--- JUDGE: Running command: {full_cmd} ---")
    
    try:
        container_output = client.containers.run(
            image="python:3.11-slim",
            command=full_cmd,
            volumes={abs_workspace_path: {'bind': '/app', 'mode': 'rw'}},
            working_dir="/app",
            remove=True,
            stdout=True,
            stderr=True
        )
        return "PASS", container_output.decode('utf-8')

    except docker.errors.ContainerError as e:
        # FIX: ContainerError stores logs in 'e.stderr' as bytes.
        # It does NOT have a 'stdout' attribute.
        logs = e.stderr.decode('utf-8') if e.stderr else "Container failed with no logs."
        print("--- JUDGE: [FAIL] Tests failed. Traceback captured. ---")
        return "FAIL", logs
    
    except Exception as e:
        return "ERROR", f"Sandbox crash: {str(e)}"