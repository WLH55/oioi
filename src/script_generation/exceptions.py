"""
Script Generation 模块异常类
"""
from src.exceptions import BusinessValidationException, HttpClientException


class ScriptGenerationError(BusinessValidationException):
    """剧本生成异常"""

    def __init__(self, reason: str = "剧本生成失败"):
        super().__init__(f"剧本生成错误: {reason}")


class CharacterGenerationError(BusinessValidationException):
    """角色生成异常"""

    def __init__(self, reason: str = "角色生成失败"):
        super().__init__(f"角色生成错误: {reason}")


class AIServiceError(HttpClientException):
    """AI 服务调用异常"""

    def __init__(self, service: str, reason: str = "AI 服务调用失败"):
        message = f"{service} 服务错误: {reason}"
        super().__init__(message)
        self.service = service
        self.reason = reason


class SceneGenerationError(BusinessValidationException):
    """场景生成异常"""

    def __init__(self, reason: str = "场景生成失败"):
        super().__init__(f"场景生成错误: {reason}")
