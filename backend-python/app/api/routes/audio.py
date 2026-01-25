from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from app.services.ffmpeg_service import FFmpegService
from app.core.response import APIResponse
from app.core.exceptions import BadRequestException
from app.core.config import settings

router = APIRouter()

# Initialize FFmpeg service
ffmpeg_service = FFmpegService(output_dir=settings.LOCAL_STORAGE_PATH)


class AudioExtractionRequest(BaseModel):
    video_path: str
    output_format: str = "mp3"
    output_path: Optional[str] = None


class BatchAudioExtractionRequest(BaseModel):
    video_paths: List[str]
    output_format: str = "mp3"


@router.post("/extract")
async def extract_audio(
    request: AudioExtractionRequest,
    background_tasks: BackgroundTasks
):
    """
    Extract audio from video
    Corresponds to Go: ExtractAudio in audio_extraction.go
    """
    try:
        result = await ffmpeg_service.extract_audio(
            video_path=request.video_path,
            output_format=request.output_format,
            output_path=request.output_path
        )

        return APIResponse.success({
            "message": "音频提取成功",
            "video_url": request.video_path,
            "audio_path": result["output_path"],
            "format": result["format"],
            "file_size": result["file_size"]
        })

    except Exception as e:
        raise BadRequestException(f"音频提取失败: {str(e)}")


@router.post("/extract/batch")
async def batch_extract_audio(
    request: BatchAudioExtractionRequest,
    background_tasks: BackgroundTasks
):
    """
    Batch extract audio from multiple videos
    Corresponds to Go: BatchExtractAudio in audio_extraction.go
    """
    try:
        results = await ffmpeg_service.batch_extract_audio(
            video_paths=request.video_paths,
            output_format=request.output_format
        )

        successful_count = sum(1 for r in results if r.get("success", False))
        failed_count = len(results) - successful_count

        return APIResponse.success({
            "message": f"批量音频提取完成",
            "total": len(results),
            "successful": successful_count,
            "failed": failed_count,
            "results": results
        })

    except Exception as e:
        raise BadRequestException(f"批量音频提取失败: {str(e)}")
