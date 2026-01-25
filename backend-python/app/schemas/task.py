from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class TaskResponse(BaseModel):
    id: str
    type: str
    status: str
    progress: int
    message: Optional[str] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    resource_id: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
