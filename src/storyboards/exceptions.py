"""
Storyboards 模块异常类
"""
from src.exceptions import BusinessValidationException


class StoryboardNotFound(BusinessValidationException):
    """分镜不存在异常"""

    def __init__(self, storyboard_id: int = None):
        message = "分镜不存在" + (f" (ID: {storyboard_id})" if storyboard_id is not None else "")
        super().__init__(message)


class StoryboardGenerationError(BusinessValidationException):
    """分镜生成异常"""

    def __init__(self, reason: str = "分镜生成失败"):
        super().__init__(f"分镜生成错误: {reason}")


class FramePromptNotFound(BusinessValidationException):
    """帧提示词不存在异常"""

    def __init__(self, prompt_id: int = None):
        message = "帧提示词不存在" + (f" (ID: {prompt_id})" if prompt_id is not None else "")
        super().__init__(message)
