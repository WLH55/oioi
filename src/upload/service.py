"""
Upload 模块业务逻辑层

处理文件上传相关功能
"""
import os
import uuid

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.character_library.models import Character
from src.utils.file import get_file_url, save_upload_file
from src.core.config import settings

from .exceptions import FileSaveException, InvalidFileTypeException
from .schemas import (
    AudioUploadResponse,
    ImageUploadResponse,
    VideoUploadResponse,
)


class UploadService:
    """文件上传服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload_image(
        self,
        file: UploadFile,
        character_id: int | None = None
    ) -> ImageUploadResponse:
        """
        上传图片文件

        Args:
            file: 上传的文件
            character_id: 可选的角色 ID，用于关联角色图片

        Returns:
            上传响应

        Raises:
            InvalidFileTypeException: 文件类型无效
            FileSaveException: 文件保存失败
        """
        # 验证文件类型
        if not file.content_type or not file.content_type.startswith("image/"):
            raise InvalidFileTypeException(file.content_type)

        # 生成唯一文件名
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{file_extension}"

        # 保存文件
        try:
            file_path = await save_upload_file(
                file,
                settings.LOCAL_STORAGE_PATH,
                filename
            )
        except Exception as e:
            raise FileSaveException(f"文件保存失败: {str(e)}")

        # 获取文件 URL
        file_url = get_file_url(filename, settings.BASE_URL)

        # 如果提供了 character_id，更新角色图片
        if character_id:
            result = await self.db.execute(
                select(Character).where(Character.id == character_id)
            )
            character = result.scalar_one_or_none()

            if character:
                character.image_url = file_url
                await self.db.commit()

        return ImageUploadResponse(
            message="图片上传成功",
            filename=filename,
            url=file_url,
            path=file_path,
            character_id=character_id
        )

    async def upload_video(self, file: UploadFile) -> VideoUploadResponse:
        """
        上传视频文件

        Args:
            file: 上传的文件

        Returns:
            上传响应

        Raises:
            InvalidFileTypeException: 文件类型无效
            FileSaveException: 文件保存失败
        """
        # 验证文件类型
        if not file.content_type or not file.content_type.startswith("video/"):
            raise InvalidFileTypeException(file.content_type)

        # 生成唯一文件名
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{file_extension}"

        # 保存文件
        try:
            file_path = await save_upload_file(
                file,
                settings.LOCAL_STORAGE_PATH,
                filename
            )
        except Exception as e:
            raise FileSaveException(f"文件保存失败: {str(e)}")

        # 获取文件 URL
        file_url = get_file_url(filename, settings.BASE_URL)

        return VideoUploadResponse(
            message="视频上传成功",
            filename=filename,
            url=file_url,
            path=file_path
        )

    async def upload_audio(self, file: UploadFile) -> AudioUploadResponse:
        """
        上传音频文件

        Args:
            file: 上传的文件

        Returns:
            上传响应

        Raises:
            InvalidFileTypeException: 文件类型无效
            FileSaveException: 文件保存失败
        """
        # 验证文件类型
        if not file.content_type or not file.content_type.startswith("audio/"):
            raise InvalidFileTypeException(file.content_type)

        # 生成唯一文件名
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{file_extension}"

        # 保存文件
        try:
            file_path = await save_upload_file(
                file,
                settings.LOCAL_STORAGE_PATH,
                filename
            )
        except Exception as e:
            raise FileSaveException(f"文件保存失败: {str(e)}")

        # 获取文件 URL
        file_url = get_file_url(filename, settings.BASE_URL)

        return AudioUploadResponse(
            message="音频上传成功",
            filename=filename,
            url=file_url,
            path=file_path
        )
