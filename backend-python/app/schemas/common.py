from pydantic import BaseModel
from typing import Optional, Dict, Any


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
