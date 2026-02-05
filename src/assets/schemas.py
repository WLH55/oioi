"""
资源请求/响应模型

定义资源相关的 Pydantic 模型。
"""
from datetime import datetime

from pydantic import BaseModel, Field


class AssetBase(BaseModel):
    """资源基础模型"""
    name: str = Field(..., min_length=1, max_length=200, description="资源名称")
    description: str | None = Field(None, description="资源描述")
    type: str = Field(..., description="资源类型（image/video/audio）")
    category: str | None = Field(None, description="分类")
    url: str = Field(..., description="资源 URL")
    thumbnail_url: str | None = Field(None, description="缩略图 URL")


class AssetCreate(AssetBase):
    """创建资源请求"""
    drama_id: int | None = Field(None, description="剧目 ID")
    episode_id: int | None = Field(None, description="集数 ID")
    storyboard_id: int | None = Field(None, description="分镜 ID")
    storyboard_num: int | None = Field(None, description="分镜编号")
    local_path: str | None = Field(None, description="本地路径")
    file_size: float | None = Field(None, description="文件大小")
    mime_type: str | None = Field(None, description="MIME 类型")
    width: int | None = Field(None, description="宽度（图片/视频）")
    height: int | None = Field(None, description="高度（图片/视频）")
    duration: int | None = Field(None, description="时长（视频/音频，秒）")
    format: str | None = Field(None, description="格式")
    image_gen_id: int | None = Field(None, description="图片生成 ID")
    video_gen_id: int | None = Field(None, description="视频生成 ID")


class AssetUpdate(BaseModel):
    """更新资源请求"""
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    category: str | None = None
    url: str | None = None
    thumbnail_url: str | None = None
    is_favorite: bool | None = None


class AssetResponse(AssetBase):
    """资源响应"""
    id: int
    drama_id: int | None
    episode_id: int | None
    storyboard_id: int | None
    storyboard_num: int | None
    local_path: str | None
    file_size: float | None
    mime_type: str | None
    width: int | None
    height: int | None
    duration: int | None
    format: str | None
    image_gen_id: int | None
    video_gen_id: int | None
    is_favorite: bool
    view_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssetImportRequest(BaseModel):
    """导入资源请求"""
    name: str = Field(..., min_length=1, max_length=200, description="资源名称")
    description: str | None = Field(None, description="资源描述")
    category: str | None = Field(None, description="分类")


class AssetImportResponse(BaseModel):
    """导入资源响应"""
    asset_id: int
    gen_id: int
    message: str
