from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class VideoGenerationBase(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=2000)
    provider: str
    model: Optional[str] = None
    duration: Optional[int] = None
    fps: Optional[int] = None
    aspect_ratio: Optional[str] = None
    style: Optional[str] = None
    motion_level: Optional[int] = None
    camera_motion: Optional[str] = None
    seed: Optional[int] = None


class VideoGenerationCreate(VideoGenerationBase):
    drama_id: str
    storyboard_id: Optional[int] = None
    image_gen_id: Optional[int] = None
    reference_mode: Optional[str] = "single"
    image_url: Optional[str] = None
    first_frame_url: Optional[str] = None
    last_frame_url: Optional[str] = None
    reference_image_urls: Optional[List[str]] = None


class VideoGenerationResponse(VideoGenerationBase):
    id: int
    drama_id: int
    storyboard_id: Optional[int] = None
    image_gen_id: Optional[int] = None
    reference_mode: Optional[str] = None
    image_url: Optional[str] = None
    first_frame_url: Optional[str] = None
    last_frame_url: Optional[str] = None
    reference_image_urls: Optional[str] = None
    resolution: Optional[str] = None
    video_url: Optional[str] = None
    local_path: Optional[str] = None
    status: str
    task_id: Optional[str] = None
    error_msg: Optional[str] = None
    completed_at: Optional[datetime] = None
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
