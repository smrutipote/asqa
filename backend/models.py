from pydantic import BaseModel
from typing import Optional, Any


class AnalyzeRequest(BaseModel):
    code: str
    language: str = "python"
    description: str = ""


class AgentEvent(BaseModel):
    agent: str
    status: str  # "running" | "completed" | "error" | "retrying"
    data: Optional[Any] = None
    message: Optional[str] = None
    retry_count: Optional[int] = None
