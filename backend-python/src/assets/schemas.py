"""
资源请求/响应模型

定义资源相关的 Pydantic 模型。
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AssetBase(BaseModel):
    """资源基础模型"""
    name: str = Field(..., min_length=1, max_length=200, description="资源名称")
    description: Optional[str] = Field(None, description="资源描述")
    type: str = Field(..., description="资源类型（image/video/audio）")
    category: Optional[str] = Field(None, description="分类")
    url: str = Field(..., description="资源 URL")
    thumbnail_url: Optional[str] = Field(None, description="缩略图 URL")


class AssetCreate(AssetBase):
    """创建资源请求"""
    drama_id: Optional[int] = Field(None, description="剧目 ID")
    episode_id: Optional[int] = Field(None, description="集数 ID")
    storyboard_id: Optional[int] = Field(None, description="分镜 ID")
    storyboard_num: Optional[int] = Field(None, description="分镜编号")
    local_path: Optional[str] = Field(None, description="本地路径")
    file_size: Optional[float] = Field(None, description="文件大小")
    mime_type: Optional[str] = Field(None, description="MIME 类型")
    width: Optional[int] = Field(None, description="宽度（图片/视频）")
    height: Optional[int] = Field(None, description="高度（图片/视频）")
    duration: Optional[int] = Field(None, description="时长（视频/音频，秒）")
    format: Optional[str] = Field(None, description="格式")
    image_gen_id: Optional[int] = Field(None, description="图片生成 ID")
    video_gen_id: Optional[int] = Field(None, description="视频生成 ID")


class AssetUpdate(BaseModel):
    """更新资源请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_favorite: Optional[bool] = None


class AssetResponse(AssetBase):
    """资源响应"""
    id: int
    drama_id: Optional[int]
    episode_id: Optional[int]
    storyboard_id: Optional[int]
    storyboard_num: Optional[int]
    local_path: Optional[str]
    file_size: Optional[float]
    mime_type: Optional[str]
    width: Optional[int]
    height: Optional[int]
    duration: Optional[int]
    format: Optional[str]
    image_gen_id: Optional[int]
    video_gen_id: Optional[int]
    is_favorite: bool
    view_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssetImportRequest(BaseModel):
    """导入资源请求"""
    name: str = Field(..., min_length=1, max_length=200, description="资源名称")
    description: Optional[str] = Field(None, description="资源描述")
    category: Optional[str] = Field(None, description="分类")


class AssetImportResponse(BaseModel):
    """导入资源响应"""
    asset_id: int
    gen_id: int
    message: str
