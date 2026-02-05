"""
Video Merges 模块请求和响应模型
"""

from pydantic import BaseModel, Field


class SceneClip(BaseModel):
    """场景片段"""
    scene_id: int = Field(..., description="场景 ID")
    video_url: str = Field(..., description="视频 URL")
    start_time: float = Field(..., description="开始时间（秒）")
    end_time: float = Field(..., description="结束时间（秒）")
    duration: float = Field(..., description="持续时间（秒）")
    order: int = Field(..., description="顺序")
    transition: dict | None = Field(None, description="转场效果")


class VideoMergeCreate(BaseModel):
    """创建视频合成请求"""
    episode_id: int = Field(..., description="章节 ID")
    drama_id: int = Field(..., description="剧目 ID")
    title: str = Field(..., min_length=1, max_length=200, description="标题")
    provider: str = Field("ffmpeg", description="提供商")
    model: str | None = Field(None, description="模型名称")
    scenes: list[SceneClip] = Field(..., min_length=1, description="场景片段列表")


class VideoMergeResponse(BaseModel):
    """视频合成响应"""
    id: int
    episode_id: int
    drama_id: int
    title: str
    provider: str
    model: str | None = None
    status: str
    scenes: list[dict] | None = None
    merged_url: str | None = None
    output_path: str | None = None
    duration: float | None = None
    file_size: int | None = None
    task_id: str | None = None
    error_msg: str | None = None
    created_at: str | None = None
    completed_at: str | None = None

    class Config:
        from_attributes = True


class VideoMergeListResponse(BaseModel):
    """视频合成列表项响应"""
    id: int
    episode_id: int
    drama_id: int
    title: str
    provider: str
    status: str
    merged_url: str | None = None
    duration: float | None = None
    task_id: str | None = None
    created_at: str | None = None
    completed_at: str | None = None

    class Config:
        from_attributes = True
