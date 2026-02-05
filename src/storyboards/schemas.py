"""
Storyboards 模块的 Pydantic 模型
"""
from datetime import datetime

from pydantic import BaseModel, Field


class StoryboardBase(BaseModel):
    """分镜基础模型"""
    storyboard_number: int = Field(..., description="分镜编号", ge=1)
    title: str | None = Field(None, description="标题", max_length=255)
    location: str | None = Field(None, description="地点", max_length=255)
    time: str | None = Field(None, description="时间", max_length=255)
    shot_type: str | None = Field(None, description="镜头类型", max_length=100)
    angle: str | None = Field(None, description="角度", max_length=100)
    movement: str | None = Field(None, description="运动", max_length=100)
    action: str | None = Field(None, description="动作")
    result: str | None = Field(None, description="结果")
    atmosphere: str | None = Field(None, description="氛围")
    dialogue: str | None = Field(None, description="对话")
    description: str | None = Field(None, description="描述")
    duration: int = Field(5, description="时长(秒)", ge=1)


class StoryboardCreate(StoryboardBase):
    """创建分镜请求模型"""
    episode_id: int = Field(..., description="集数ID")
    scene_id: int | None = Field(None, description="场景ID")


class StoryboardUpdate(BaseModel):
    """更新分镜请求模型"""
    title: str | None = Field(None, description="标题", max_length=255)
    location: str | None = Field(None, description="地点", max_length=255)
    time: str | None = Field(None, description="时间", max_length=255)
    shot_type: str | None = Field(None, description="镜头类型", max_length=100)
    angle: str | None = Field(None, description="角度", max_length=100)
    movement: str | None = Field(None, description="运动", max_length=100)
    action: str | None = Field(None, description="动作")
    result: str | None = Field(None, description="结果")
    atmosphere: str | None = Field(None, description="氛围")
    image_prompt: str | None = Field(None, description="图片提示词")
    video_prompt: str | None = Field(None, description="视频提示词")
    bgm_prompt: str | None = Field(None, description="背景音乐提示词")
    sound_effect: str | None = Field(None, description="音效", max_length=255)
    dialogue: str | None = Field(None, description="对话")
    description: str | None = Field(None, description="描述")
    duration: int | None = Field(None, description="时长(秒)", ge=1)
    video_url: str | None = Field(None, description="视频URL")
    status: str | None = Field(None, description="状态")


class StoryboardResponse(StoryboardBase):
    """分镜响应模型"""
    id: int
    drama_id: int
    episode_id: int
    scene_id: int | None = None
    image_prompt: str | None = None
    video_prompt: str | None = None
    bgm_prompt: str | None = None
    sound_effect: str | None = None
    composed_image: str | None = None
    video_url: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StoryboardListResponse(BaseModel):
    """分镜列表响应模型"""
    total: int
    items: list[StoryboardResponse]


class FramePromptBase(BaseModel):
    """帧提示词基础模型"""
    frame_type: str = Field(..., description="帧类型", max_length=20)
    prompt: str = Field(..., description="提示词")


class FramePromptCreate(FramePromptBase):
    """创建帧提示词请求模型"""
    storyboard_id: int = Field(..., description="分镜ID")


class FramePromptResponse(FramePromptBase):
    """帧提示词响应模型"""
    id: int
    storyboard_id: int
    description: str | None = None
    layout: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FramePromptListResponse(BaseModel):
    """帧提示词列表响应模型"""
    storyboard_id: int
    frame_prompts: list[FramePromptResponse]
    count: int


class StoryboardGenerationRequest(BaseModel):
    """分镜生成请求模型"""
    style: str | None = Field(None, description="视觉风格")
    aspect_ratio: str = Field("16:9", description="宽高比")
    num_shots_per_scene: int = Field(3, description="每场景镜头数", ge=1, le=10)


class StoryboardGenerationResponse(BaseModel):
    """分镜生成响应模型"""
    message: str
    episode_id: int
    task_id: str
    status: str
