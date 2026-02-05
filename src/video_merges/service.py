"""
Video Merges 模块业务逻辑层
"""
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.schemas import PageResponse
from src.ffmpeg import FFmpegService

from src.episodes.models import Episode
from src.video_merges.models import VideoMerge

from .exceptions import EpisodeNotFoundException, VideoMergeNotFoundException
from .schemas import VideoMergeCreate, VideoMergeListResponse, VideoMergeResponse


class VideoMergeService:
    """视频合成服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ffmpeg_service = FFmpegService(output_dir=settings.LOCAL_STORAGE_PATH)

    async def list_merges(
        self,
        page: int = 1,
        page_size: int = 20,
        episode_id: int = None,
        status_filter: str = None
    ) -> PageResponse[list[VideoMergeListResponse]]:
        """
        获取视频合成列表

        Args:
            page: 页码
            page_size: 每页大小
            episode_id: 章节 ID 过滤
            status_filter: 状态过滤

        Returns:
            分页响应
        """
        query = select(VideoMerge)

        # 应用过滤条件
        if episode_id:
            query = query.where(VideoMerge.episode_id == episode_id)
        if status_filter:
            query = query.where(VideoMerge.status == status_filter)

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # 获取分页结果
        skip = (page - 1) * page_size
        query = query.offset(skip).limit(page_size).order_by(VideoMerge.created_at.desc())
        result = await self.db.execute(query)
        merges = result.scalars().all()

        # 转换为响应模型
        items = [
            VideoMergeListResponse(
                id=merge.id,
                episode_id=merge.episode_id,
                drama_id=merge.drama_id,
                title=merge.title,
                provider=merge.provider,
                status=merge.status,
                merged_url=merge.merged_url,
                duration=merge.duration,
                task_id=merge.task_id,
                created_at=merge.created_at.isoformat() if merge.created_at else None,
                completed_at=merge.completed_at.isoformat() if merge.completed_at else None
            )
            for merge in merges
        ]

        return PageResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size
        )

    async def create_merge(
        self,
        merge_request: VideoMergeCreate
    ) -> VideoMergeResponse:
        """
        创建视频合成任务

        Args:
            merge_request: 合成请求

        Returns:
            创建的视频合成记录
        """
        # 验证章节存在
        episode_result = await self.db.execute(
            select(Episode).where(Episode.id == merge_request.episode_id)
        )
        episode = episode_result.scalar_one_or_none()

        if not episode:
            raise EpisodeNotFoundException(merge_request.episode_id)

        # 生成任务 ID
        task_id = f"video_merge_{uuid.uuid4().hex[:8]}"

        # 生成输出路径
        output_filename = f"episode_{merge_request.episode_id}_merged.mp4"
        output_path = f"{settings.LOCAL_STORAGE_PATH}/{output_filename}"

        # 创建视频合成记录
        db_merge = VideoMerge(
            episode_id=merge_request.episode_id,
            drama_id=merge_request.drama_id,
            title=merge_request.title,
            provider=merge_request.provider,
            model=merge_request.model,
            scenes=[scene.model_dump() for scene in merge_request.scenes],
            status=VideoMergeStatus.PROCESSING.value,
            task_id=task_id,
            output_path=output_path
        )

        self.db.add(db_merge)
        await self.db.commit()
        await self.db.refresh(db_merge)

        return VideoMergeResponse.model_validate(db_merge)

    async def get_merge(self, merge_id: int) -> VideoMergeResponse:
        """
        获取视频合成详情

        Args:
            merge_id: 视频合成 ID

        Returns:
            视频合成详情
        """
        result = await self.db.execute(
            select(VideoMerge).where(VideoMerge.id == merge_id)
        )
        merge = result.scalar_one_or_none()

        if not merge:
            raise VideoMergeNotFoundException(merge_id)

        return VideoMergeResponse.model_validate(merge)

    async def delete_merge(self, merge_id: int) -> None:
        """
        删除视频合成记录

        Args:
            merge_id: 视频合成 ID
        """
        result = await self.db.execute(
            select(VideoMerge).where(VideoMerge.id == merge_id)
        )
        merge = result.scalar_one_or_none()

        if not merge:
            raise VideoMergeNotFoundException(merge_id)

        await self.db.delete(merge)
        await self.db.commit()


async def process_video_merge_task(merge_id: int, scenes: list[dict], output_path: str):
    """
    处理视频合成的后台任务

    Args:
        merge_id: 视频合成 ID
        scenes: 场景片段列表
        output_path: 输出路径
    """
    from src.database import async_session_maker
    from src.utils.file import get_file_url

    try:
        # 使用 FFmpeg 合成视频
        ffmpeg_service = FFmpegService(output_dir=settings.LOCAL_STORAGE_PATH)
        result = await ffmpeg_service.merge_videos(
            video_clips=scenes,
            output_path=output_path
        )

        # 更新数据库结果
        async with async_session_maker() as db:
            merge_result = await db.execute(
                select(VideoMerge).where(VideoMerge.id == merge_id)
            )
            db_merge = merge_result.scalar_one_or_none()

            if db_merge:
                if result.get("success"):
                    # 生成合成视频的 URL
                    merged_url = get_file_url(
                        output_path.split("/")[-1],
                        settings.BASE_URL
                    )

                    db_merge.status = VideoMergeStatus.COMPLETED.value
                    db_merge.merged_url = merged_url
                    db_merge.duration = result.get("total_duration", 0)
                    db_merge.file_size = result.get("file_size", 0)
                    from sqlalchemy import func
                    db_merge.completed_at = func.now()
                else:
                    db_merge.status = VideoMergeStatus.FAILED.value
                    db_merge.error_msg = "视频合成失败"

                await db.commit()

    except Exception as e:
        # 更新错误状态
        async with async_session_maker() as db:
            merge_result = await db.execute(
                select(VideoMerge).where(VideoMerge.id == merge_id)
            )
            db_merge = merge_result.scalar_one_or_none()

            if db_merge:
                db_merge.status = VideoMergeStatus.FAILED.value
                db_merge.error_msg = str(e)
                await db.commit()
