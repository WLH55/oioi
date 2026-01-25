from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class DramaBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    genre: Optional[str] = None
    style: str = "realistic"
    total_episodes: int = 1
    total_duration: int = 0
    tags: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class DramaCreate(DramaBase):
    pass


class DramaUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    genre: Optional[str] = None
    style: Optional[str] = None
    total_episodes: Optional[int] = None
    total_duration: Optional[int] = None
    status: Optional[str] = None
    thumbnail: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class DramaResponse(DramaBase):
    id: int
    status: str
    thumbnail: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CharacterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    role: Optional[str] = None
    description: Optional[str] = None
    appearance: Optional[str] = None
    personality: Optional[str] = None
    voice_style: Optional[str] = None
    seed_value: Optional[str] = None
    sort_order: int = 0


class CharacterCreate(CharacterBase):
    drama_id: int


class CharacterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[str] = None
    description: Optional[str] = None
    appearance: Optional[str] = None
    personality: Optional[str] = None
    voice_style: Optional[str] = None
    image_url: Optional[str] = None
    seed_value: Optional[str] = None
    sort_order: Optional[int] = None


class CharacterResponse(CharacterBase):
    id: int
    drama_id: int
    image_url: Optional[str] = None
    reference_images: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EpisodeBase(BaseModel):
    episode_number: int
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    duration: int = 0


class EpisodeCreate(EpisodeBase):
    drama_id: int
    script_content: Optional[str] = None


class EpisodeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    script_content: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    status: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail: Optional[str] = None


class EpisodeResponse(EpisodeBase):
    id: int
    drama_id: int
    script_content: Optional[str] = None
    status: str
    video_url: Optional[str] = None
    thumbnail: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SceneBase(BaseModel):
    location: str = Field(..., max_length=200)
    time: str = Field(..., max_length=100)
    prompt: str
    storyboard_count: int = 1


class SceneCreate(SceneBase):
    drama_id: int
    episode_id: Optional[int] = None


class SceneUpdate(BaseModel):
    location: Optional[str] = None
    time: Optional[str] = None
    prompt: Optional[str] = None
    storyboard_count: Optional[int] = None
    image_url: Optional[str] = None
    status: Optional[str] = None


class SceneResponse(SceneBase):
    id: int
    drama_id: int
    episode_id: Optional[int] = None
    image_url: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StoryboardBase(BaseModel):
    storyboard_number: int
    title: Optional[str] = None
    location: Optional[str] = None
    time: Optional[str] = None
    shot_type: Optional[str] = None
    angle: Optional[str] = None
    movement: Optional[str] = None
    action: Optional[str] = None
    result: Optional[str] = None
    atmosphere: Optional[str] = None
    dialogue: Optional[str] = None
    description: Optional[str] = None
    duration: int = 5


class StoryboardCreate(StoryboardBase):
    episode_id: int
    scene_id: Optional[int] = None


class StoryboardUpdate(BaseModel):
    title: Optional[str] = None
    location: Optional[str] = None
    time: Optional[str] = None
    shot_type: Optional[str] = None
    angle: Optional[str] = None
    movement: Optional[str] = None
    action: Optional[str] = None
    result: Optional[str] = None
    atmosphere: Optional[str] = None
    image_prompt: Optional[str] = None
    video_prompt: Optional[str] = None
    bgm_prompt: Optional[str] = None
    sound_effect: Optional[str] = None
    dialogue: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    video_url: Optional[str] = None
    status: Optional[str] = None


class StoryboardResponse(StoryboardBase):
    id: int
    episode_id: int
    scene_id: Optional[int] = None
    image_prompt: Optional[str] = None
    video_prompt: Optional[str] = None
    bgm_prompt: Optional[str] = None
    sound_effect: Optional[str] = None
    composed_image: Optional[str] = None
    video_url: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
