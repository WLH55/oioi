"""
Audio 模块路由

提供音频处理相关的 API 端点
"""
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends

from src.core.schemas import ApiResponse

from .dependencies import get_audio_service
from .schemas import (
    AudioExtractionRequest,
    AudioExtractionResponse,
    BatchAudioExtractionRequest,
    BatchAudioExtractionResponse,
)
from .service import AudioService

router = APIRouter(prefix="/audio", tags=["Audio"])


@router.post(
    "/extract",
    summary="提取音频",
    description="从视频中提取音频"
)
async def extract_audio(
    request: AudioExtractionRequest,
    background_tasks: BackgroundTasks,
    service: Annotated[AudioService, Depends(get_audio_service)]
) -> ApiResponse[AudioExtractionResponse]:
    """
    从视频中提取音频

    - **video_path**: 视频文件路径
    - **output_format**: 输出音频格式（默认 mp3）
    - **output_path**: 可选的输出路径
    """
    result = await service.extract_audio(
        video_path=request.video_path,
        output_format=request.output_format,
        output_path=request.output_path
    )
    return ApiResponse(data=result)


@router.post(
    "/extract/batch",
    summary="批量提取音频",
    description="从多个视频中批量提取音频"
)
async def batch_extract_audio(
    request: BatchAudioExtractionRequest,
    background_tasks: BackgroundTasks,
    service: Annotated[AudioService, Depends(get_audio_service)]
) -> ApiResponse[BatchAudioExtractionResponse]:
    """
    批量从视频中提取音频

    - **video_paths**: 视频文件路径列表
    - **output_format**: 输出音频格式（默认 mp3）
    """
    result = await service.batch_extract_audio(
        video_paths=request.video_paths,
        output_format=request.output_format
    )
    return ApiResponse(data=result)
