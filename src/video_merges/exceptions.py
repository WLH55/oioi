"""
Video Merges 模块自定义异常
"""
from src.exceptions import BusinessValidationException


class VideoMergeNotFoundException(BusinessValidationException):
    """视频合成记录不存在异常"""

    def __init__(self, merge_id: int = None):
        message = "视频合成记录不存在" + (f" (ID: {merge_id})" if merge_id else "")
        super().__init__(message)


class EpisodeNotFoundException(BusinessValidationException):
    """章节不存在异常"""

    def __init__(self, episode_id: int = None):
        message = "章节不存在" + (f" (ID: {episode_id})" if episode_id else "")
        super().__init__(message)


class VideoMergeException(BusinessValidationException):
    """视频合成异常"""

    def __init__(self, message: str = "视频合成失败"):
        super().__init__(message)
