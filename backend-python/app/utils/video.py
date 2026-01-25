import asyncio
import subprocess
import os
from typing import Optional, Dict
import re
from app.utils.logger import log
from app.core.config import settings


class VideoProcessor:
    """Video processing utilities using FFmpeg"""

    def __init__(self):
        self.ffmpeg_path = "ffmpeg"  # Assumes ffmpeg is in PATH

    async def extract_audio(
        self,
        video_path: str,
        output_path: str,
        output_format: str = "mp3",
        sample_rate: int = 44100
    ) -> bool:
        """
        Extract audio from video file

        Args:
            video_path: Path to input video file
            output_path: Path to output audio file
            output_format: Audio format (mp3, wav, etc.)
            sample_rate: Audio sample rate

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

            # Build ffmpeg command
            command = [
                self.ffmpeg_path,
                "-i", video_path,
                "-vn",  # Don't include video
                "-ar", str(sample_rate),  # Sample rate
                "-ac", "2",  # Stereo
                "-b:a", "192k",  # Bitrate
                output_path
            ]

            # Run ffmpeg
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                log.info(f"Audio extracted successfully: {output_path}")
                return True
            else:
                log.error(f"FFmpeg error: {stderr.decode()}")
                return False

        except Exception as e:
            log.error(f"Error extracting audio: {str(e)}")
            return False

    async def merge_videos(
        self,
        video_paths: list[str],
        output_path: str,
        transition_duration: float = 0.5,
        transition_type: str = "fade"
    ) -> bool:
        """
        Merge multiple video files

        Args:
            video_paths: List of input video file paths
            output_path: Path to output video file
            transition_duration: Duration of transitions in seconds
            transition_type: Type of transition (fade, crossfade, etc.)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

            if len(video_paths) == 0:
                log.error("No video paths provided")
                return False

            # For simple concatenation without transitions
            if transition_type == "none" or transition_duration == 0:
                # Create concat list file
                concat_file = output_path + ".txt"
                with open(concat_file, "w") as f:
                    for video_path in video_paths:
                        f.write(f"file '{os.path.abspath(video_path)}'\n")

                # Run ffmpeg concat
                command = [
                    self.ffmpeg_path,
                    "-f", "concat",
                    "-safe", "0",
                    "-i", concat_file,
                    "-c", "copy",
                    output_path
                ]

                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                stdout, stderr = await process.communicate()

                # Clean up concat file
                if os.path.exists(concat_file):
                    os.remove(concat_file)

                if process.returncode == 0:
                    log.info(f"Videos merged successfully: {output_path}")
                    return True
                else:
                    log.error(f"FFmpeg error: {stderr.decode()}")
                    return False

            else:
                # For videos with transitions, use xfade filter
                # This is more complex - simplified version for 2 videos
                if len(video_paths) != 2:
                    log.warning("Transitions only supported for 2 videos in this implementation")
                    # Fall back to simple concat
                    return await self.merge_videos(video_paths, output_path, 0, "none")

                # Crossfade two videos
                command = [
                    self.ffmpeg_path,
                    "-i", video_paths[0],
                    "-i", video_paths[1],
                    "-filter_complex",
                    f"[0:v][1:v]xfade=transition={transition_type}:duration={transition_duration}:offset=0[vout]",
                    "-map", "[vout]",
                    "-c:v", "libx264",
                    "-preset", "fast",
                    output_path
                ]

                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                stdout, stderr = await process.communicate()

                if process.returncode == 0:
                    log.info(f"Videos merged with transition: {output_path}")
                    return True
                else:
                    log.error(f"FFmpeg error: {stderr.decode()}")
                    return False

        except Exception as e:
            log.error(f"Error merging videos: {str(e)}")
            return False

    async def get_video_info(self, video_path: str) -> Optional[dict]:
        """
        Get video file information

        Args:
            video_path: Path to video file

        Returns:
            Dict with video info (duration, width, height, codec, etc.)
        """
        try:
            command = [
                self.ffmpeg_path,
                "-i", video_path,
                "-f", "null",
                "-"
            ]

            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            output = stderr.decode()

            # Parse output to extract info
            info = {}

            # Extract duration
            duration_match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', output)
            if duration_match:
                hours, minutes, seconds = duration_match.groups()
                info['duration'] = int(hours) * 3600 + int(minutes) * 60 + float(seconds)

            # Extract resolution
            resolution_match = re.search(r'(\d+)x(\d+)', output)
            if resolution_match:
                info['width'] = int(resolution_match.group(1))
                info['height'] = int(resolution_match.group(2))

            # Extract FPS
            fps_match = re.search(r'(\d+\.?\d*) fps', output)
            if fps_match:
                info['fps'] = float(fps_match.group(1))

            return info

        except Exception as e:
            log.error(f"Error getting video info: {str(e)}")
            return None

    async def compress_video(
        self,
        input_path: str,
        output_path: str,
        crf: int = 23,
        preset: str = "medium"
    ) -> bool:
        """
        Compress video file

        Args:
            input_path: Input video file path
            output_path: Output video file path
            crf: Constant Rate Factor (0-51, lower = better quality)
            preset: Compression preset

        Returns:
            True if successful, False otherwise
        """
        try:
            command = [
                self.ffmpeg_path,
                "-i", input_path,
                "-vcodec", "libx264",
                "-crf", str(crf),
                "-preset", preset,
                "-acodec", "aac",
                "-b:a", "128k",
                output_path
            ]

            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                log.info(f"Video compressed successfully: {output_path}")
                return True
            else:
                log.error(f"FFmpeg error: {stderr.decode()}")
                return False

        except Exception as e:
            log.error(f"Error compressing video: {str(e)}")
            return False


# Singleton instance
_video_processor = None


def get_video_processor() -> VideoProcessor:
    """Get video processor singleton"""
    global _video_processor
    if _video_processor is None:
        _video_processor = VideoProcessor()
    return _video_processor
