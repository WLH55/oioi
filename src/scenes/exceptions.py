"""
Scenes 模块异常类
"""
from src.exceptions import BusinessValidationException


class SceneNotFound(BusinessValidationException):
    """场景不存在异常"""

    def __init__(self, scene_id: int = None):
        message = "场景不存在" + (f" (ID: {scene_id})" if scene_id is not None else "")
        super().__init__(message)


class SceneGenerationError(BusinessValidationException):
    """场景图片生成异常"""

    def __init__(self, reason: str = "图片生成失败"):
        super().__init__(f"场景图片生成错误: {reason}")
