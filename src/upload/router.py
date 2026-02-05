"""
Upload 模块路由

提供文件上传相关的 API 端点
"""
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from src.core.schemas import ApiResponse

from .dependencies import get_upload_service
from .schemas import AudioUploadResponse, ImageUploadResponse, VideoUploadResponse
from .service import UploadService

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post(
    "/image",
    summary="上传图片",
    description="上传图片文件，可选择性关联到角色"
)
async def upload_image(
    service: Annotated[UploadService, Depends(get_upload_service)],
    file: Annotated[UploadFile, File(...)],
    character_id: int | None = Form(None)
) -> ApiResponse[ImageUploadResponse]:
    """
    上传图片文件

    - **file**: 图片文件
    - **character_id**: 可选的角色 ID，用于关联角色图片
    """
    result = await service.upload_image(file, character_id)
    return ApiResponse(data=result)


@router.post(
    "/video",
    summary="上传视频",
    description="上传视频文件"
)
async def upload_video(
    service: Annotated[UploadService, Depends(get_upload_service)],
    file: Annotated[UploadFile, File(...)]
) -> ApiResponse[VideoUploadResponse]:
    """
    上传视频文件

    - **file**: 视频文件
    """
    result = await service.upload_video(file)
    return ApiResponse(data=result)


@router.post(
    "/audio",
    summary="上传音频",
    description="上传音频文件"
)
async def upload_audio(
    service: Annotated[UploadService, Depends(get_upload_service)],
    file: Annotated[UploadFile, File(...)]
) -> ApiResponse[AudioUploadResponse]:
    """
    上传音频文件

    - **file**: 音频文件
    """
    result = await service.upload_audio(file)
    return ApiResponse(data=result)
