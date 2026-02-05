"""
全局异常处理器

定义项目中所有自定义异常和系统异常的处理逻辑，
将异常转换为统一的 ApiResponse 格式返回给客户端。
"""
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.exceptions import BusinessValidationException, HttpClientException
from src.core.schemas import ApiResponse, ResponseCode


async def business_validation_exception_handler(
    request: Request,
    exc: BusinessValidationException
) -> JSONResponse:
    """
    处理业务参数验证异常

    当请求参数不符合业务规则时触发，
    返回 400 Bad Request 和错误消息。

    Args:
        request: FastAPI 请求对象
        exc: 业务验证异常

    Returns:
        JSONResponse: 统一格式的错误响应
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ApiResponse.error(
            code=ResponseCode.BAD_REQUEST,
            message=exc.message or "参数验证失败"
        ).model_dump()
    )


async def httpclient_exception_handler(
    request: Request,
    exc: HttpClientException
) -> JSONResponse:
    """
    处理 HTTP 客户端异常

    当第三方 API 调用失败时触发，
    使用异常中的状态码或默认 500。

    Args:
        request: FastAPI 请求对象
        exc: HTTP 客户端异常

    Returns:
        JSONResponse: 统一格式的错误响应
    """
    return JSONResponse(
        status_code=exc.code or status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ApiResponse.error(
            code=exc.code or ResponseCode.INTERNAL_ERROR,
            message=exc.message
        ).model_dump()
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    处理所有未捕获的异常

    作为最后的异常处理器，捕获所有未被其他处理器处理的异常。

    Args:
        request: FastAPI 请求对象
        exc: 通用异常

    Returns:
        JSONResponse: 统一格式的错误响应
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ApiResponse.error(
            code=ResponseCode.INTERNAL_ERROR,
            message=str(exc) or "服务器内部错误"
        ).model_dump()
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    处理 Pydantic 验证异常

    当请求体或参数验证失败时触发，
    返回详细的验证错误信息。

    Args:
        request: FastAPI 请求对象
        exc: 请求验证异常

    Returns:
        JSONResponse: 统一格式的错误响应
    """
    # 格式化验证错误信息
    errors = exc.errors()
    error_messages = []
    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"])
        msg = error["msg"]
        error_messages.append(f"{field}: {msg}")

    error_message = "; ".join(error_messages)

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ApiResponse.error(
            code=ResponseCode.BAD_REQUEST,
            message=error_message or "请求参数验证失败"
        ).model_dump()
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
) -> JSONResponse:
    """
    处理 Starlette HTTP 异常

    处理 FastAPI/Starlette 内部抛出的 HTTP 异常。

    Args:
        request: FastAPI 请求对象
        exc: Starlette HTTP 异常

    Returns:
        JSONResponse: 统一格式的错误响应
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse.error(
            code=exc.status_code,
            message=exc.detail or "HTTP 错误"
        ).model_dump()
    )


def register_exception_handlers(app) -> None:
    """
    注册所有异常处理器到 FastAPI 应用

    Args:
        app: FastAPI 应用实例
    """
    app.add_exception_handler(BusinessValidationException, business_validation_exception_handler)
    app.add_exception_handler(HttpClientException, httpclient_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
