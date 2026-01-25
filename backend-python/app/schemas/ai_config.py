from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class AIServiceConfigBase(BaseModel):
    service_type: str = Field(..., pattern="^(text|image|video)$")
    name: str = Field(..., min_length=1, max_length=100)
    provider: str
    base_url: str
    model: List[str]
    endpoint: Optional[str] = None
    query_endpoint: Optional[str] = None
    priority: int = 0
    is_default: bool = False
    settings: Optional[str] = None


class AIServiceConfigCreate(AIServiceConfigBase):
    api_key: str


class AIServiceConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    provider: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[List[str]] = None
    endpoint: Optional[str] = None
    query_endpoint: Optional[str] = None
    priority: Optional[int] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    settings: Optional[str] = None


class AIServiceConfigResponse(AIServiceConfigBase):
    id: int
    api_key: str  # In production, you might want to mask this
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TestConnectionRequest(BaseModel):
    base_url: str
    api_key: str
    model: List[str]
    provider: Optional[str] = None
    endpoint: Optional[str] = None
