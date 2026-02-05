"""
角色库模块特定异常

定义角色库相关的自定义异常类。
"""
from src.exceptions import BusinessValidationException


class CharacterNotFound(BusinessValidationException):
    """角色未找到异常"""

    def __init__(self, character_id: int = None):
        message = "角色不存在" + (f" (ID: {character_id})" if character_id else "")
        super().__init__(message)


class CharacterLibraryNotFound(BusinessValidationException):
    """角色库项未找到异常"""

    def __init__(self, item_id: int = None):
        message = "角色库项不存在" + (f" (ID: {item_id})" if item_id else "")
        super().__init__(message)


class CharacterHasNoImage(BusinessValidationException):
    """角色没有图片异常"""

    def __init__(self):
        message = "角色没有图片，无法添加到角色库"
        super().__init__(message)
