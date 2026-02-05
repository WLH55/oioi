"""
Images 模块请求和响应模型
"""
from datetime import datetime

from pydantic import BaseModel, Field


class ImageGenerationCreate(BaseModel):
    """创建图片生成请求"""
    prompt: str = Field(..., min_length=5, max_length=2000, description="图片生成提示词")
    negative_prompt: str | None = Field(None, max_length=1000, description="负面提示词")
    provider: str = Field(..., description="AI 提供商")
    model: str = Field(..., description="模型名称")
    size: str = Field("1024x1024", description="图片尺寸")
    quality: str = Field("standard", description="图片质量")
    style: str | None = Field(None, description="图片风格")
    steps: int | None = Field(None, ge=1, le=100, description="生成步数")
    cfg_scale: float | None = Field(None, ge=0, le=20, description="CFG 权重")
    seed: int | None = Field(None, ge=0, description="随机种子")
    width: int | None = Field(None, gt=0, description="图片宽度")
    height: int | None = Field(None, gt=0, description="图片高度")
    reference_images: list[str] | None = Field(None, description="参考图片 URL 列表")
    drama_id: str = Field(..., description="剧目 ID")
    storyboard_id: int | None = Field(None, description="分镜 ID")
    scene_id: int | None = Field(None, description="场景 ID")
    character_id: int | None = Field(None, description="角色 ID")
    image_type: str | None = Field("storyboard", description="图片类型")
    frame_type: str | None = Field(None, description="帧类型")


class ImageGenerationResponse(BaseModel):
    """图片生成响应"""
    id: int
    drama_id: int
    storyboard_id: int | None = None
    scene_id: int | None = None
    character_id: int | None = None
    image_type: str
    frame_type: str | None = None
    provider: str
    prompt: str
    negative_prompt: str | None = None
    model: str
    size: str
    quality: str
    style: str | None = None
    steps: int | None = None
    cfg_scale: float | None = None
    seed: int | None = None
    image_url: str | None = None
    local_path: str | None = None
    status: str
    error_msg: str | None = None
    width: int | None = None
    height: int | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True


class ImageListResponse(BaseModel):
    """图片列表项响应"""
    id: int
    storyboard_id: int | None = None
    drama_id: int
    scene_id: int | None = None
    character_id: int | None = None
    image_type: str
    frame_type: str | None = None
    provider: str
    prompt: str
    model: str
    size: str
    quality: str
    style: str | None = None
    steps: int | None = None
    cfg_scale: float | None = None
    seed: int | None = None
    image_url: str | None = None
    local_path: str | None = None
    status: str
    error_msg: str | None = None
    width: int | None = None
    height: int | None = None
    created_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True


class BackgroundImageResponse(BaseModel):
    """场景背景图片响应"""
    scene_id: int
    location: str | None = None
    time: str | None = None
    image_url: str | None = None
    local_path: str | None = None
    image_gen_id: int
