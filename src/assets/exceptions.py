"""
资源模块特定异常

定义资源相关的自定义异常类。
"""
from src.exceptions import BusinessValidationException


class AssetNotFound(BusinessValidationException):
    """资源未找到异常"""

    def __init__(self, asset_id: int = None):
        message = "资源不存在" + (f" (ID: {asset_id})" if asset_id else "")
        super().__init__(message)


class ImageGenerationNotFound(BusinessValidationException):
    """图片生成记录未找到异常"""

    def __init__(self, gen_id: int = None):
        message = "图片生成记录不存在" + (f" (ID: {gen_id})" if gen_id else "")
        super().__init__(message)


class VideoGenerationNotFound(BusinessValidationException):
    """视频生成记录未找到异常"""

    def __init__(self, gen_id: int = None):
        message = "视频生成记录不存在" + (f" (ID: {gen_id})" if gen_id else "")
        super().__init__(message)


class GenerationHasNoUrl(BusinessValidationException):
    """生成记录没有 URL 异常"""

    def __init__(self, gen_type: str = "生成记录"):
        message = f"{gen_type}没有 URL，无法导入为资源"
        super().__init__(message)


class InvalidAssetType(BusinessValidationException):
    """无效的资源类型异常"""

    def __init__(self, asset_type: str):
        message = f"无效的资源类型: {asset_type}，支持的类型: image, video, audio"
        super().__init__(message)
