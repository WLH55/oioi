"""
Images 模块自定义异常
"""
from src.exceptions import BusinessValidationException


class ImageGenerationNotFoundException(BusinessValidationException):
    """图片生成记录不存在异常"""

    def __init__(self, image_id: int = None):
        message = "图片生成记录不存在" + (f" (ID: {image_id})" if image_id else "")
        super().__init__(message)


class SceneNotFoundException(BusinessValidationException):
    """场景不存在异常"""

    def __init__(self, scene_id: int = None):
        message = "场景不存在" + (f" (ID: {scene_id})" if scene_id else "")
        super().__init__(message)


class EpisodeNotFoundException(BusinessValidationException):
    """章节不存在异常"""

    def __init__(self, episode_id: int = None):
        message = "章节不存在" + (f" (ID: {episode_id})" if episode_id else "")
        super().__init__(message)
