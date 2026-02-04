"""
自定义异常类

定义项目中使用的自定义异常类型，用于业务验证和 HTTP 客户端错误。
"""
from typing import Optional


class HttpClientException(Exception):
    """
    HTTP 客户端异常

    用于第三方 API 调用失败的场景。

    Attributes:
        message: 错误消息
        code: HTTP 状态码（可选）

    Example:
        >>> raise HttpClientException("AI 服务调用失败", code=503)
    """
    def __init__(self, message: str, code: Optional[int] = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class BusinessValidationException(Exception):
    """
    业务参数验证异常

    用于请求参数不符合业务规则的场景。
    此异常会被全局异常处理器捕获并转换为 ApiResponse 格式。

    Attributes:
        message: 错误消息
        code: 错误码（可选，默认为 400）

    Example:
        >>> if quantity <= 0:
        ...     raise BusinessValidationException("数量必须大于 0")
    """
    def __init__(self, message: str, code: Optional[int] = None):
        self.message = message
        self.code = code
        super().__init__(self.message)
