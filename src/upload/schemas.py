"""
Upload 模块请求和响应模型
"""

from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    """图片上传响应"""
    message: str
    filename: str
    url: str
    path: str
    character_id: int | None = None


class VideoUploadResponse(BaseModel):
    """视频上传响应"""
    message: str
    filename: str
    url: str
    path: str


class AudioUploadResponse(BaseModel):
    """音频上传响应"""
    message: str
    filename: str
    url: str
    path: str


class FileUploadResponse(BaseModel):
    """通用文件上传响应"""
    message: str
    filename: str
    url: str
    path: str
    file_type: str
    file_size: int | None = None
