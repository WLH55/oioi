"""
Episodes 模块的 Pydantic 模型
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EpisodeBase(BaseModel):
    """集数基础模型"""
    episode_number: int = Field(..., description="集数编号", ge=1)
    title: str = Field(..., description="集数标题", max_length=200)
    description: str | None = Field(None, description="集数描述")
    script_content: str | None = Field(None, description="剧本内容")
    duration: int | None = Field(0, description="时长(秒)", ge=0)


class EpisodeCreate(EpisodeBase):
    """创建集数请求模型"""
    drama_id: int = Field(..., description="剧目ID")


class EpisodeUpdate(BaseModel):
    """更新集数请求模型"""
    title: str | None = Field(None, description="集数标题", max_length=200)
    description: str | None = Field(None, description="集数描述")
    script_content: str | None = Field(None, description="剧本内容")
    duration: int | None = Field(None, description="时长(秒)", ge=0)
    status: str | None = Field(None, description="状态")
    video_url: str | None = Field(None, description="视频URL")
    thumbnail: str | None = Field(None, description="缩略图URL")


class EpisodeResponse(EpisodeBase):
    """集数响应模型"""
    id: int
    drama_id: int
    status: str
    video_url: str | None = None
    thumbnail: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EpisodeDetailResponse(EpisodeResponse):
    """集数详情响应模型"""
    drama_title: str | None = None
    storyboard_count: int = 0
    scene_count: int = 0


class EpisodeFinalizeRequest(BaseModel):
    """完成集数制作请求模型"""
    timeline_data: dict[str, Any] | None = Field(
        None,
        description="时间线数据，包含视频片段信息"
    )


class EpisodeFinalizeResponse(BaseModel):
    """完成集数制作响应模型"""
    message: str
    episode_id: int
    task_id: str
    status: str


class EpisodeDownloadResponse(BaseModel):
    """集数下载响应模型"""
    video_url: str
    title: str
    episode_number: int
    duration: int
    status: str


class EpisodeListResponse(BaseModel):
    """集数列表响应模型"""
    total: int
    items: list[EpisodeResponse]
