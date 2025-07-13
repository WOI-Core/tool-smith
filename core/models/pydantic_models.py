# core/models/pydantic_models.py
from pydantic import BaseModel, Field
from typing import Optional

class TaskRequest(BaseModel):
    content_name: str = Field(..., examples=["BFS Algorithm"])
    cases_size: int = Field(..., gt=0, examples=[10])
    detail: Optional[str] = Field(None, examples=["The graph is always connected."])