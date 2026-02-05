"""
剧目请求/响应模型

定义剧目相关的 Pydantic 模型。
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

# ========== 剧目模型 ==========

class DramaBase(BaseModel):
    """剧目基础模型"""
    title: str = Field(..., min_length=1, max_length=200, description="剧目标题")
    description: str | None = Field(None, description="剧目描述")
    genre: str | None = Field(None, description="类型")
    style: str = Field(default="realistic", description="风格")
    total_episodes: int = Field(default=1, ge=1, description="总集数")
    total_duration: int = Field(default=0, ge=0, description="总时长（秒）")
    tags: dict[str, Any] | None = Field(None, description="标签")
    metadata: dict[str, Any] | None = Field(None, description="元数据")


class DramaCreate(DramaBase):
    """创建剧目请求"""
    pass


class DramaUpdate(BaseModel):
    """更新剧目请求"""
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    genre: str | None = None
    style: str | None = None
    total_episodes: int | None = Field(None, ge=1)
    total_duration: int | None = Field(None, ge=0)
    status: str | None = None
    thumbnail: str | None = None
    tags: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class DramaResponse(DramaBase):
    """剧目响应"""
    id: int
    status: str
    thumbnail: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 角色模型 ==========

class CharacterBase(BaseModel):
    """角色基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="角色名称")
    role: str | None = Field(None, description="角色类型")
    description: str | None = Field(None, description="角色描述")
    appearance: str | None = Field(None, description="外貌")
    personality: str | None = Field(None, description="性格")
    voice_style: str | None = Field(None, description="声音风格")
    seed_value: str | None = Field(None, description="种子值")
    sort_order: int = Field(default=0, ge=0, description="排序")


class CharacterCreate(CharacterBase):
    """创建角色请求"""
    drama_id: int = Field(..., description="剧目 ID")


class CharacterUpdate(BaseModel):
    """更新角色请求"""
    name: str | None = Field(None, min_length=1, max_length=100)
    role: str | None = None
    description: str | None = None
    appearance: str | None = None
    personality: str | None = None
    voice_style: str | None = None
    image_url: str | None = None
    reference_images: list[str] | None = None
    seed_value: str | None = None
    sort_order: int | None = Field(None, ge=0)


class CharacterResponse(CharacterBase):
    """角色响应"""
    id: int
    drama_id: int
    image_url: str | None = None
    reference_images: list[str] | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 集数模型 ==========

class EpisodeBase(BaseModel):
    """集数基础模型"""
    episode_number: int = Field(..., ge=1, description="集数编号")
    title: str = Field(..., min_length=1, max_length=200, description="标题")
    description: str | None = Field(None, description="描述")
    duration: int = Field(default=0, ge=0, description="时长（秒）")


class EpisodeCreate(EpisodeBase):
    """创建集数请求"""
    drama_id: int = Field(..., description="剧目 ID")
    script_content: str | None = Field(None, description="剧本内容")


class EpisodeUpdate(BaseModel):
    """更新集数请求"""
    title: str | None = Field(None, min_length=1, max_length=200)
    script_content: str | None = None
    description: str | None = None
    duration: int | None = Field(None, ge=0)
    status: str | None = None
    video_url: str | None = None
    thumbnail: str | None = None


class EpisodeResponse(EpisodeBase):
    """集数响应"""
    id: int
    drama_id: int
    script_content: str | None = None
    status: str
    video_url: str | None = None
    thumbnail: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 剧目统计模型 ==========

class DramaStats(BaseModel):
    """剧目统计"""
    total_dramas: int = Field(..., description="总剧目数")
    total_episodes: int = Field(..., description="总集数")
    total_characters: int = Field(..., description="总角色数")
    status_breakdown: dict[str, int] = Field(default_factory=dict, description="状态分布")
    completed_dramas: int = Field(..., description="已完成剧目数")
    in_progress: int = Field(..., description="进行中剧目数")


# ========== 保存请求模型 ==========

class BatchCharactersSave(BaseModel):
    """批量保存角色请求"""
    characters: list[dict[str, Any]] = Field(..., description="角色列表")


class BatchEpisodesSave(BaseModel):
    """批量保存集数请求"""
    episodes: list[dict[str, Any]] = Field(..., description="集数列表")


class OutlineSave(BaseModel):
    """大纲保存请求"""
    outline: dict[str, Any] = Field(..., description="大纲数据")


class ProgressSave(BaseModel):
    """进度保存请求"""
    progress: dict[str, Any] = Field(..., description="进度数据")
    status: str | None = Field(None, description="状态")
