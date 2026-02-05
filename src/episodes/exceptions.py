"""
Episodes 模块异常类
"""
from src.exceptions import BusinessValidationException


class EpisodeNotFound(BusinessValidationException):
    """集数不存在异常"""

    def __init__(self, episode_id: int = None):
        message = "集数不存在" + (f" (ID: {episode_id})" if episode_id is not None else "")
        super().__init__(message)


class EpisodeNotFinalizable(BusinessValidationException):
    """集数无法完成异常"""

    def __init__(self, reason: str = "该集数没有可用的视频片段"):
        super().__init__(f"无法完成集数制作: {reason}")


class EpisodeHasNoVideo(BusinessValidationException):
    """集数没有视频异常"""

    def __init__(self, episode_id: int = None):
        message = "该剧集还没有生成视频"
        if episode_id is not None:
            message += f" (ID: {episode_id})"
        super().__init__(message)
