"""
FFmpeg 服务模块

提供 FFmpeg 封装服务，用于视频处理。
"""
import subprocess
import os
from typing import Optional

from src.core.config import settings


class FFmpegService:
    """FFmpeg 服务类"""

    def __init__(self, output_dir: str = "./uploads"):
        self.output_dir = output_dir
        self.ffmpeg_path = "ffmpeg"

    def get_video_info(self, video_path: str) -> dict:
        """
        获取视频信息

        Args:
            video_path: 视频文件路径

        Returns:
            包含视频信息的字典
        """
        import json

        cmd = [
            self.ffmpeg_path,
            "-i", video_path,
            "-f", "ffmetadata",
            "-f", "json", "-"
        ]
        # 简化的实现，实际应使用 ffprobe
        return {"path": video_path}

    def extract_audio(
        self,
        video_path: str,
        output_path: str,
        format: str = "mp3",
        start_time: Optional[float] = None,
        duration: Optional[float] = None
    ) -> str:
        """
        从视频中提取音频

        Args:
            video_path: 视频文件路径
            output_path: 输出文件路径
            format: 输出音频格式
            start_time: 开始时间（秒）
            duration: 持续时间（秒）

        Returns:
            输出文件路径
        """
        cmd = [self.ffmpeg_path, "-y"]

        if start_time is not None:
            cmd.extend(["-ss", str(start_time)])
        if duration is not None:
            cmd.extend(["-t", str(duration)])

        cmd.extend([
            "-i", video_path,
            "-vn",
            "-acodec", "libmp3lame" if format == "mp3" else "aac",
            output_path
        ])

        subprocess.run(cmd, check=True)
        return output_path

    def merge_videos(self, video_paths: list[str], output_path: str) -> str:
        """
        合并多个视频

        Args:
            video_paths: 视频文件路径列表
            output_path: 输出文件路径

        Returns:
            输出文件路径
        """
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            for path in video_paths:
                f.write(f"file '{os.path.abspath(path)}'\n")
            list_path = f.name

        try:
            cmd = [
                self.ffmpeg_path, "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", list_path,
                "-c", "copy",
                output_path
            ]
            subprocess.run(cmd, check=True)
        finally:
            os.unlink(list_path)

        return output_path


__all__ = ["FFmpegService"]
