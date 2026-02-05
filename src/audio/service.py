"""
Audio 模块业务逻辑层

使用 FFmpeg 服务处理音频提取
"""

from src.config import settings
from src.ffmpeg import FFmpegService

from .exceptions import AudioExtractionException
from .schemas import AudioExtractionResponse, BatchAudioExtractionItem, BatchAudioExtractionResponse


class AudioService:
    """音频处理服务类"""

    def __init__(self):
        self.ffmpeg_service = FFmpegService(output_dir=settings.LOCAL_STORAGE_PATH)

    async def extract_audio(
        self,
        video_path: str,
        output_format: str = "mp3",
        output_path: str = None
    ) -> AudioExtractionResponse:
        """
        从视频中提取音频

        Args:
            video_path: 视频文件路径
            output_format: 输出音频格式
            output_path: 可选的输出路径

        Returns:
            音频提取响应

        Raises:
            AudioExtractionException: 提取失败时抛出
        """
        try:
            result = await self.ffmpeg_service.extract_audio(
                video_path=video_path,
                output_format=output_format,
                output_path=output_path
            )

            return AudioExtractionResponse(
                message="音频提取成功",
                video_url=video_path,
                audio_path=result["output_path"],
                format=result["format"],
                file_size=result["file_size"]
            )

        except Exception as e:
            raise AudioExtractionException(f"音频提取失败: {str(e)}")

    async def batch_extract_audio(
        self,
        video_paths: list[str],
        output_format: str = "mp3"
    ) -> BatchAudioExtractionResponse:
        """
        批量从视频中提取音频

        Args:
            video_paths: 视频文件路径列表
            output_format: 输出音频格式

        Returns:
            批量音频提取响应
        """
        try:
            results = await self.ffmpeg_service.batch_extract_audio(
                video_paths=video_paths,
                output_format=output_format
            )

            successful_count = sum(1 for r in results if r.get("success", False))
            failed_count = len(results) - successful_count

            # 转换结果格式
            formatted_results = [
                BatchAudioExtractionItem(
                    video_path=r.get("video_path", ""),
                    success=r.get("success", False),
                    audio_path=r.get("audio_path"),
                    error=r.get("error")
                )
                for r in results
            ]

            return BatchAudioExtractionResponse(
                message="批量音频提取完成",
                total=len(results),
                successful=successful_count,
                failed=failed_count,
                results=formatted_results
            )

        except Exception as e:
            raise AudioExtractionException(f"批量音频提取失败: {str(e)}")
