from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
class FilePlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path: str = Field(description="Path to the file, e.g., 'src/weather_cli/cli.py'")
    description: str = Field(description="What this file does")
class FunctionSpec(BaseModel):
    # This nested model MUST also have extra="forbid"
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(description="Name of the function")
    signature: str = Field(description="The full function signature (e.g., def add(a: int, b: int) -> int)")
    behavior: str = Field(description="Description of what the function should do")


class TechnicalSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    project_name: str
    # ADD THIS LINE BACK:
    file_structure: List[FilePlan] = Field(description="List of files to be created")
    functions: List[FunctionSpec]
    setup_commands: List[str]
    env_vars: Optional[List[str]] = Field(default_factory=list)


class ForgeState(BaseModel):
    requirement: str
    spec: Optional[TechnicalSpec] = None
    test_code: Optional[str] = None
    source_code: Optional[str] = None
    logs: List[str] = []
    iteration: int = 0
    is_secure: bool = False
    context_from_db: Optional[str] = ""
