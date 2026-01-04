# FORGE: Automated AI Engineering Pipeline

**FORGE** is an automated AI engineering framework designed to build, test, and harden multi-file software projects using a coordinated pipeline of specialized AI agents.

---

## 🚀 Key Features

- **Multi-Agent Orchestration**  
  Utilizes a structured workflow involving Architect, Developer, SQA, and Auditor agents to handle the full software development lifecycle.

- **Vector Memory**  
  Integrates with **Qdrant** to provide semantic search capabilities, allowing agents to understand existing repository context before starting new tasks.

- **Isolated Sandboxing**  
  Uses Docker to run a *Judge* node that executes tests in a safe, isolated environment to verify code integrity.

- **Adversarial Hardening**  
  Includes a dedicated Auditor agent that identifies security flaws and logic holes, writing exploit tests that the Developer must pass.

- **Structured Outputs**  
  Leverages **Pydantic schemas** to ensure consistent and valid communication between different stages of the engineering pipeline.

---

## 🛠️ The Agent Team

- **Architect (GPT-5 Mini)**  
  Designs the modular system architecture and generates a `TechnicalSpec` including file structures and function signatures.

- **Blind SQA**  
  Creates a comprehensive Pytest suite based solely on the Architect’s specification, ensuring unbiased testing.

- **Lead Developer**  
  Implements the code for each file and refactors it based on test failures or auditor feedback.

- **Auditor**  
  Acts as an adversarial peer, identifying edge cases and vulnerabilities to harden the codebase.

---

## 🏗️ Workflow Architecture

The project follows a **StateGraph** workflow defined in `main.py`:

1. **Architect** — Generates the blueprint  
2. **SQA** — Drafts the test suite  
3. **Lead Developer** — Writes the initial implementation  
4. **Judge** — Runs tests inside a Docker container  
5. **Router**
   - If tests fail → returns to Lead Developer  
   - If tests pass → moves to Auditor  
6. **Cycle** — Iterates until the project is hardened and passes all refined tests

---

## ⚙️ Prerequisites

- Python **3.11+**
- Docker & Docker Compose
- OpenAI API Key
- Qdrant (Vector Database)

---

## 📥 Installation

### Clone the repository
```bash
git clone https://github.com/sanvibhowmick/FORGE
cd forge
```
## 📥 Installation

### Install dependencies
```bash
pip install -r requirements.txt
```
🔧 Configure Environment Variables

Create a .env file in the root directory:
```
OPENAI_API_KEY=your_key_here
QDRANT_URL=http://localhost:6333
```
▶️ Start Required Services
```
docker-compose up -d
```

🚀 Usage

To start a new project build, run the orchestrator:
```
python main.py
```


You will be prompted to describe what you want FORGE to build.
The system will then initialize a ./workspace directory and begin the engineering pipeline.

📂 Project Structure
```
agents/        # Logic for specialized AI agents
utils/         # Core utilities (workspace, memory, Docker judge)
workspace/     # Directory where agents generate and test code
schema.py      # Pydantic models for project state and specifications
main.py        # Entry point and LangGraph workflow definition
```
