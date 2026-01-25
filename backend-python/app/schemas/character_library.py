from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CharacterLibraryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = None
    image_url: str
    description: Optional[str] = None
    tags: Optional[str] = None
    source_type: str = "generated"


class CharacterLibraryCreate(CharacterLibraryBase):
    pass


class CharacterLibraryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    source_type: Optional[str] = None


class CharacterLibraryResponse(CharacterLibraryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CharacterImageGenerate(BaseModel):
    provider: str
    model: str
    prompt: str
    negative_prompt: Optional[str] = None
    size: str = "1024x1024"
    style: Optional[str] = None


class BatchCharacterImageGenerate(BaseModel):
    character_ids: list[int]
    provider: str
    model: str
    size: str = "1024x1024"
    style: Optional[str] = None
