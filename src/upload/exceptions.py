"""
Upload 模块自定义异常
"""
from src.exceptions import HttpClientException


class FileUploadException(HttpClientException):
    """文件上传异常"""

    def __init__(self, message: str = "文件上传失败"):
        super().__init__(message=message)


class InvalidFileTypeException(HttpClientException):
    """无效文件类型异常"""

    def __init__(self, file_type: str = None):
        message = "无效的文件类型"
        if file_type:
            message += f": {file_type}"
        super().__init__(message=message)


class FileSaveException(HttpClientException):
    """文件保存异常"""

    def __init__(self, message: str = "文件保存失败"):
        super().__init__(message=message)
