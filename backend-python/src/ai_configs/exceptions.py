"""
AI 配置模块特定异常

定义 AI 配置相关的自定义异常类。
"""
from src.exceptions import BusinessValidationException


class AIConfigNotFound(BusinessValidationException):
    """AI 配置未找到异常"""

    def __init__(self, config_id: int = None):
        message = f"AI 配置不存在" + (f" (ID: {config_id})" if config_id else "")
        super().__init__(message)


class InvalidServiceType(BusinessValidationException):
    """无效的服务类型异常"""

    def __init__(self, service_type: str):
        message = f"无效的服务类型: {service_type}，必须是 text、image 或 video"
        super().__init__(message)


class DuplicateDefaultConfig(BusinessValidationException):
    """重复的默认配置异常"""

    def __init__(self, service_type: str):
        message = f"服务类型 {service_type} 已存在默认配置"
        super().__init__(message)
