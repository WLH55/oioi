"""
剧目模块特定异常

定义剧目相关的自定义异常类。
"""
from src.exceptions import BusinessValidationException


class DramaNotFound(BusinessValidationException):
    """剧目未找到异常"""

    def __init__(self, drama_id: int = None):
        message = "剧目不存在" + (f" (ID: {drama_id})" if drama_id else "")
        super().__init__(message)


class EpisodeNotFound(BusinessValidationException):
    """集数未找到异常"""

    def __init__(self, episode_id: int = None):
        message = "集数不存在" + (f" (ID: {episode_id})" if episode_id else "")
        super().__init__(message)


class CharacterNotFound(BusinessValidationException):
    """角色未找到异常"""

    def __init__(self, character_id: int = None):
        message = "角色不存在" + (f" (ID: {character_id})" if character_id else "")
        super().__init__(message)


class InvalidEpisodeNumber(BusinessValidationException):
    """无效的集数编号异常"""

    def __init__(self, episode_number: int):
        message = f"无效的集数编号: {episode_number}"
        super().__init__(message)


class EpisodeAlreadyExists(BusinessValidationException):
    """集数已存在异常"""

    def __init__(self, drama_id: int, episode_number: int):
        message = f"剧目 (ID: {drama_id}) 的第 {episode_number} 集已存在"
        super().__init__(message)
