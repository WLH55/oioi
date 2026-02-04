"""
角色库请求/响应模型

定义角色库相关的 Pydantic 模型。
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CharacterLibraryBase(BaseModel):
    """角色库基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="角色名称")
    category: Optional[str] = Field(None, description="分类")
    image_url: str = Field(..., description="角色图片 URL")
    description: Optional[str] = Field(None, description="角色描述")
    tags: Optional[str] = Field(None, description="标签")
    source_type: str = Field(default="generated", description="来源类型")


class CharacterLibraryCreate(CharacterLibraryBase):
    """创建角色库项请求"""
    pass


class CharacterLibraryUpdate(BaseModel):
    """更新角色库项请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    source_type: Optional[str] = None


class CharacterLibraryResponse(CharacterLibraryBase):
    """角色库响应"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CharacterImageGenerate(BaseModel):
    """生成角色图片请求"""
    provider: str = Field(..., description="AI 提供商")
    model: str = Field(..., description="模型名称")
    prompt: str = Field(..., description="提示词")
    negative_prompt: Optional[str] = Field(None, description="负向提示词")
    size: str = Field(default="1024x1024", description="图片尺寸")
    style: Optional[str] = Field(None, description="风格")


class BatchCharacterImageGenerate(BaseModel):
    """批量生成角色图片请求"""
    character_ids: list[int] = Field(..., description="角色 ID 列表")
    provider: str = Field(..., description="AI 提供商")
    model: str = Field(..., description="模型名称")
    size: str = Field(default="1024x1024", description="图片尺寸")
    style: Optional[str] = Field(None, description="风格")
