"""
FFmpeg service for audio extraction and video processing
"""
import os
import subprocess
import logging
from typing import Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class FFmpegService:
    """Service for FFmpeg operations"""

    def __init__(self, output_dir: str = "./data/outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    async def extract_audio(
        self,
        video_path: str,
        output_format: str = "mp3",
        output_path: Optional[str] = None
    ) -> dict:
        """
        Extract audio from video file

        Args:
            video_path: Path or URL to video file
            output_format: Output audio format (mp3, wav, aac, etc.)
            output_path: Optional output path

        Returns:
            Dict with audio file info
        """
        try:
            # Generate output path if not provided
            if not output_path:
                video_name = Path(video_path).stem
                output_path = os.path.join(
                    self.output_dir,
                    f"{video_name}_audio.{output_format}"
                )

            # FFmpeg command for audio extraction
            command = [
                "ffmpeg",
                "-i", video_path,
                "-vn",  # No video
                "-acodec", self._get_audio_codec(output_format),
                "-ab", "192k",  # Audio bitrate
                "-ar", "44100",  # Sample rate
                "-y",  # Overwrite output file
                output_path
            ]

            logger.info(f"Extracting audio from {video_path}")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                raise Exception(f"Audio extraction failed: {result.stderr}")

            # Get file size
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

            logger.info(f"Audio extracted successfully to {output_path}")

            return {
                "output_path": output_path,
                "format": output_format,
                "file_size": file_size,
                "success": True
            }

        except subprocess.TimeoutExpired:
            logger.error("FFmpeg timeout")
            raise Exception("Audio extraction timeout")
        except Exception as e:
            logger.error(f"Failed to extract audio: {str(e)}")
            raise

    async def batch_extract_audio(
        self,
        video_paths: List[str],
        output_format: str = "mp3"
    ) -> List[dict]:
        """
        Batch extract audio from multiple videos

        Args:
            video_paths: List of video paths/URLs
            output_format: Output audio format

        Returns:
            List of extraction results
        """
        results = []

        for video_path in video_paths:
            try:
                result = await self.extract_audio(video_path, output_format)
                results.append({
                    "video_path": video_path,
                    "result": result,
                    "success": True
                })
            except Exception as e:
                logger.error(f"Failed to extract audio from {video_path}: {str(e)}")
                results.append({
                    "video_path": video_path,
                    "error": str(e),
                    "success": False
                })

        return results

    async def merge_videos(
        self,
        video_clips: List[dict],
        output_path: str,
        transition_duration: float = 0.5
    ) -> dict:
        """
        Merge multiple video clips into one

        Args:
            video_clips: List of video clip dicts with keys:
                - video_url: Path or URL to video
                - start_time: Start time in seconds
                - end_time: End time in seconds
                - duration: Clip duration
                - order: Clip order in merge
            output_path: Output video path
            transition_duration: Duration of transition between clips

        Returns:
            Dict with merged video info
        """
        try:
            # Sort clips by order
            sorted_clips = sorted(video_clips, key=lambda x: x.get("order", 0))

            # Create concat list for FFmpeg
            concat_file = os.path.join(self.output_dir, "concat_list.txt")
            with open(concat_file, "w") as f:
                for clip in sorted_clips:
                    video_path = clip.get("video_url", "")
                    # For URLs, we need to download first or use -i directly
                    f.write(f"file '{video_path}'\n")

            # Calculate total duration
            total_duration = sum(clip.get("duration", 0) for clip in sorted_clips)

            # FFmpeg command for concatenation
            command = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c", "copy",  # Copy streams without re-encoding
                "-y",
                output_path
            ]

            logger.info(f"Merging {len(sorted_clips)} video clips")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )

            # Clean up concat file
            if os.path.exists(concat_file):
                os.remove(concat_file)

            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                raise Exception(f"Video merge failed: {result.stderr}")

            # Get file size
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

            logger.info(f"Videos merged successfully to {output_path}")

            return {
                "output_path": output_path,
                "total_duration": total_duration,
                "clip_count": len(sorted_clips),
                "file_size": file_size,
                "success": True
            }

        except subprocess.TimeoutExpired:
            logger.error("FFmpeg timeout")
            raise Exception("Video merge timeout")
        except Exception as e:
            logger.error(f"Failed to merge videos: {str(e)}")
            raise

    def _get_audio_codec(self, format: str) -> str:
        """Get FFmpeg audio codec for format"""
        codec_map = {
            "mp3": "libmp3lame",
            "wav": "pcm_s16le",
            "aac": "aac",
            "m4a": "aac",
            "ogg": "libvorbis",
            "flac": "flac"
        }
        return codec_map.get(format.lower(), "libmp3lame")

    async def get_video_info(self, video_path: str) -> dict:
        """
        Get video file information using ffprobe

        Args:
            video_path: Path to video file

        Returns:
            Dict with video info
        """
        try:
            command = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                logger.error(f"FFprobe error: {result.stderr}")
                raise Exception(f"Failed to get video info: {result.stderr}")

            import json
            info = json.loads(result.stdout)

            # Extract relevant info
            video_stream = next(
                (s for s in info.get("streams", []) if s.get("codec_type") == "video"),
                None
            )
            audio_stream = next(
                (s for s in info.get("streams", []) if s.get("codec_type") == "audio"),
                None
            )

            return {
                "duration": float(info.get("format", {}).get("duration", 0)),
                "width": int(video_stream.get("width", 0)) if video_stream else 0,
                "height": int(video_stream.get("height", 0)) if video_stream else 0,
                "fps": eval(video_stream.get("r_frame_rate", "0/1")) if video_stream else 0,
                "has_audio": audio_stream is not None,
                "codec": video_stream.get("codec_name") if video_stream else None,
                "format": info.get("format", {}).get("format_name")
            }

        except Exception as e:
            logger.error(f"Failed to get video info: {str(e)}")
            raise
