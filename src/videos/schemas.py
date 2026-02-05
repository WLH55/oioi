"""
Videos 模块请求和响应模型
"""
from datetime import datetime

from pydantic import BaseModel, Field


class VideoGenerationCreate(BaseModel):
    """创建视频生成请求"""
    prompt: str = Field(..., min_length=5, max_length=2000, description="视频生成提示词")
    provider: str = Field(..., description="AI 提供商")
    model: str = Field(..., description="模型名称")
    reference_mode: str | None = Field("single", description="参考模式")
    image_url: str | None = Field(None, description="参考图片 URL")
    first_frame_url: str | None = Field(None, description="首帧 URL")
    last_frame_url: str | None = Field(None, description="尾帧 URL")
    reference_image_urls: list[str] | None = Field(None, description="参考图片 URL 列表")
    duration: int | None = Field(5, ge=1, le=60, description="视频时长（秒）")
    fps: int | None = Field(30, ge=1, le=60, description="帧率")
    aspect_ratio: str | None = Field("16:9", description="宽高比")
    style: str | None = Field(None, description="视频风格")
    motion_level: int | None = Field(None, ge=1, le=10, description="运动强度")
    camera_motion: str | None = Field(None, description="相机运动")
    seed: int | None = Field(None, ge=0, description="随机种子")
    drama_id: str = Field(..., description="剧目 ID")
    storyboard_id: int | None = Field(None, description="分镜 ID")
    image_gen_id: int | None = Field(None, description="图片生成 ID")


class VideoGenerationResponse(BaseModel):
    """视频生成响应"""
    id: int
    storyboard_id: int | None = None
    drama_id: int
    image_gen_id: int | None = None
    provider: str
    prompt: str
    model: str
    reference_mode: str | None = None
    image_url: str | None = None
    first_frame_url: str | None = None
    last_frame_url: str | None = None
    reference_image_urls: str | None = None
    duration: int | None = None
    fps: int | None = None
    resolution: str | None = None
    aspect_ratio: str | None = None
    style: str | None = None
    motion_level: int | None = None
    camera_motion: str | None = None
    seed: int | None = None
    video_url: str | None = None
    minio_url: str | None = None
    local_path: str | None = None
    status: str
    task_id: str | None = None
    error_msg: str | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    width: int | None = None
    height: int | None = None

    class Config:
        from_attributes = True


class VideoListResponse(BaseModel):
    """视频列表项响应"""
    id: int
    storyboard_id: int | None = None
    drama_id: int
    image_gen_id: int | None = None
    provider: str
    prompt: str
    model: str
    reference_mode: str | None = None
    image_url: str | None = None
    first_frame_url: str | None = None
    last_frame_url: str | None = None
    duration: int | None = None
    fps: int | None = None
    resolution: str | None = None
    aspect_ratio: str | None = None
    style: str | None = None
    video_url: str | None = None
    status: str
    error_msg: str | None = None
    created_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True
