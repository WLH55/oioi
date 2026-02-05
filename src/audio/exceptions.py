"""
Audio 模块自定义异常
"""
from src.exceptions import BusinessValidationException


class AudioExtractionException(BusinessValidationException):
    """音频提取异常"""

    def __init__(self, message: str = "音频提取失败"):
        super().__init__(message)
