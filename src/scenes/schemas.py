"""
Scenes 模块的 Pydantic 模型
"""
from datetime import datetime

from pydantic import BaseModel, Field


class SceneBase(BaseModel):
    """场景基础模型"""
    location: str = Field(..., description="地点", max_length=200)
    time: str = Field(..., description="时间", max_length=100)
    prompt: str = Field(..., description="提示词")
    storyboard_count: int = Field(1, description="分镜数量", ge=1)


class SceneCreate(SceneBase):
    """创建场景请求模型"""
    drama_id: int = Field(..., description="剧目ID")
    episode_id: int | None = Field(None, description="集数ID")


class SceneUpdate(BaseModel):
    """更新场景请求模型"""
    location: str | None = Field(None, description="地点", max_length=200)
    time: str | None = Field(None, description="时间", max_length=100)
    prompt: str | None = Field(None, description="提示词")
    storyboard_count: int | None = Field(None, description="分镜数量", ge=1)
    image_url: str | None = Field(None, description="图片URL")
    status: str | None = Field(None, description="状态")


class SceneResponse(SceneBase):
    """场景响应模型"""
    id: int
    drama_id: int
    episode_id: int | None = None
    image_url: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SceneDetailResponse(SceneResponse):
    """场景详情响应模型"""
    drama_title: str | None = None
    episode_title: str | None = None


class ScenePromptUpdate(BaseModel):
    """更新场景提示词请求模型"""
    prompt: str = Field(..., description="新的提示词")


class SceneImageGenerationResponse(BaseModel):
    """场景图片生成响应模型"""
    message: str
    scene_id: int
    task_id: str
    status: str
