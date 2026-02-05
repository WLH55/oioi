"""
Audio 模块依赖注入
"""

from .service import AudioService


async def get_audio_service() -> AudioService:
    """
    获取音频服务实例

    Returns:
        音频服务实例
    """
    return AudioService()
