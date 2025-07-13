# core/models/graph_models.py
from typing import TypedDict, List, Dict
from .pydantic_models import TaskRequest

class GraphState(TypedDict):
    """Represents the state of our graph."""
    request: TaskRequest
    llm_output: str
    task_name: str
    files: List[Dict[str, str]]
    error: str