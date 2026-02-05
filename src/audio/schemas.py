"""
Audio 模块请求和响应模型
"""

from pydantic import BaseModel, Field


class AudioExtractionRequest(BaseModel):
    """音频提取请求"""
    video_path: str = Field(..., description="视频文件路径")
    output_format: str = Field("mp3", description="输出音频格式")
    output_path: str | None = Field(None, description="输出文件路径")


class BatchAudioExtractionRequest(BaseModel):
    """批量音频提取请求"""
    video_paths: list[str] = Field(..., min_length=1, description="视频文件路径列表")
    output_format: str = Field("mp3", description="输出音频格式")


class AudioExtractionResponse(BaseModel):
    """音频提取响应"""
    message: str
    video_url: str
    audio_path: str
    format: str
    file_size: int


class BatchAudioExtractionItem(BaseModel):
    """批量音频提取项"""
    video_path: str
    success: bool
    audio_path: str | None = None
    error: str | None = None


class BatchAudioExtractionResponse(BaseModel):
    """批量音频提取响应"""
    message: str
    total: int
    successful: int
    failed: int
    results: list[BatchAudioExtractionItem]
