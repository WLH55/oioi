from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.image_generation import ImageType


class ImageGenerationBase(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=2000)
    negative_prompt: Optional[str] = None
    provider: str
    model: str
    size: str
    quality: str
    style: Optional[str] = None
    steps: Optional[int] = None
    cfg_scale: Optional[float] = None
    seed: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    reference_images: Optional[List[str]] = None


class ImageGenerationCreate(ImageGenerationBase):
    drama_id: str
    storyboard_id: Optional[int] = None
    scene_id: Optional[int] = None
    character_id: Optional[int] = None
    image_type: Optional[str] = ImageType.STORYBOARD.value
    frame_type: Optional[str] = None


class ImageGenerationResponse(ImageGenerationBase):
    id: int
    drama_id: int
    storyboard_id: Optional[int] = None
    scene_id: Optional[int] = None
    character_id: Optional[int] = None
    image_type: str
    frame_type: Optional[str] = None
    image_url: Optional[str] = None
    local_path: Optional[str] = None
    status: str
    task_id: Optional[str] = None
    error_msg: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
