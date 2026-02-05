"""
Video Merges 模块

提供视频合成相关的功能
"""
from .router import router
from .schemas import SceneClip, VideoMergeCreate, VideoMergeListResponse, VideoMergeResponse
from .service import VideoMergeService

__all__ = [
    "router",
    "VideoMergeService",
    "VideoMergeCreate",
    "VideoMergeResponse",
    "VideoMergeListResponse",
    "SceneClip"
]
