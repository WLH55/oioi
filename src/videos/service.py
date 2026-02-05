"""
Videos 模块业务逻辑层
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import BusinessValidationException
from src.core.schemas import PageResponse

from src.episodes.models import Episode
from src.storyboards.models import Storyboard
from src.images.models import ImageGeneration
from src.videos.models import VideoGeneration

from .exceptions import (
    EpisodeNotFoundException,
    ImageGenerationNotFoundException,
    VideoGenerationNotFoundException,
)
from .schemas import VideoGenerationCreate, VideoGenerationResponse, VideoListResponse


class VideoGenerationService:
    """视频生成服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_generations(
        self,
        page: int = 1,
        page_size: int = 20,
        drama_id: int | None = None,
        storyboard_id: int | None = None,
        status_filter: str | None = None
    ) -> PageResponse[list[VideoListResponse]]:
        """
        获取视频生成列表

        Args:
            page: 页码
            page_size: 每页大小
            drama_id: 剧目 ID 过滤
            storyboard_id: 分镜 ID 过滤
            status_filter: 状态过滤

        Returns:
            分页响应
        """
        query = select(VideoGeneration)

        # 应用过滤条件
        if drama_id:
            query = query.where(VideoGeneration.drama_id == drama_id)
        if storyboard_id:
            query = query.where(VideoGeneration.storyboard_id == storyboard_id)
        if status_filter:
            query = query.where(VideoGeneration.status == status_filter)

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # 获取分页结果
        skip = (page - 1) * page_size
        query = query.offset(skip).limit(page_size).order_by(VideoGeneration.created_at.desc())
        result = await self.db.execute(query)
        generations = result.scalars().all()

        # 转换为响应模型
        items = [
            VideoListResponse(
                id=gen.id,
                storyboard_id=gen.storyboard_id,
                drama_id=gen.drama_id,
                image_gen_id=gen.image_gen_id,
                provider=gen.provider,
                prompt=gen.prompt,
                model=gen.model,
                reference_mode=gen.reference_mode,
                image_url=gen.image_url,
                first_frame_url=gen.first_frame_url,
                last_frame_url=gen.last_frame_url,
                duration=gen.duration,
                fps=gen.fps,
                resolution=gen.resolution,
                aspect_ratio=gen.aspect_ratio,
                style=gen.style,
                video_url=gen.video_url,
                status=gen.status,
                error_msg=gen.error_msg,
                created_at=gen.created_at,
                completed_at=gen.completed_at
            )
            for gen in generations
        ]

        return PageResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size
        )

    async def create_generation(
        self,
        request: VideoGenerationCreate
    ) -> VideoGenerationResponse:
        """
        创建视频生成任务

        Args:
            request: 创建请求

        Returns:
            创建的视频生成记录
        """
        # 验证剧目存在
        from app.models.drama import Drama
        result = await self.db.execute(
            select(Drama).where(Drama.id == int(request.drama_id))
        )
        drama = result.scalar_one_or_none()
        if not drama:
            raise BusinessValidationException(f"剧目不存在 (ID: {request.drama_id})")

        # 创建视频生成记录
        db_gen = VideoGeneration(
            drama_id=int(request.drama_id),
            storyboard_id=request.storyboard_id,
            image_gen_id=request.image_gen_id,
            provider=request.provider,
            prompt=request.prompt,
            model=request.model,
            reference_mode=request.reference_mode,
            image_url=request.image_url,
            first_frame_url=request.first_frame_url,
            last_frame_url=request.last_frame_url,
            reference_image_urls=str(request.reference_image_urls) if request.reference_image_urls else None,
            duration=request.duration,
            fps=request.fps,
            aspect_ratio=request.aspect_ratio,
            style=request.style,
            motion_level=request.motion_level,
            camera_motion=request.camera_motion,
            seed=request.seed,
            status="pending"
        )

        self.db.add(db_gen)
        await self.db.commit()
        await self.db.refresh(db_gen)

        return VideoGenerationResponse.model_validate(db_gen)

    async def get_generation(self, gen_id: int) -> VideoGenerationResponse:
        """
        获取视频生成详情

        Args:
            gen_id: 视频生成 ID

        Returns:
            视频生成详情
        """
        result = await self.db.execute(
            select(VideoGeneration).where(VideoGeneration.id == gen_id)
        )
        gen = result.scalar_one_or_none()

        if not gen:
            raise VideoGenerationNotFoundException(gen_id)

        return VideoGenerationResponse.model_validate(gen)

    async def delete_generation(self, gen_id: int) -> None:
        """
        删除视频生成记录

        Args:
            gen_id: 视频生成 ID
        """
        result = await self.db.execute(
            select(VideoGeneration).where(VideoGeneration.id == gen_id)
        )
        gen = result.scalar_one_or_none()

        if not gen:
            raise VideoGenerationNotFoundException(gen_id)

        await self.db.delete(gen)
        await self.db.commit()

    async def create_from_image(
        self,
        image_gen_id: int,
        prompt: str | None = None,
        provider: str = "doubao",
        duration: int = 5
    ) -> VideoGenerationResponse:
        """
        从图片生成创建视频

        Args:
            image_gen_id: 图片生成 ID
            prompt: 可选的自定义提示词
            provider: AI 提供商
            duration: 视频时长

        Returns:
            创建的视频生成记录
        """
        # 验证图片生成存在
        result = await self.db.execute(
            select(ImageGeneration).where(ImageGeneration.id == image_gen_id)
        )
        image_gen = result.scalar_one_or_none()

        if not image_gen:
            raise ImageGenerationNotFoundException(image_gen_id)

        # 创建视频生成记录
        db_gen = VideoGeneration(
            drama_id=image_gen.drama_id,
            storyboard_id=image_gen.storyboard_id,
            image_gen_id=image_gen.id,
            provider=provider,
            prompt=prompt or f"Video based on image: {image_gen.prompt}",
            model="default",
            reference_mode="image",
            image_url=image_gen.image_url,
            first_frame_url=image_gen.image_url,
            duration=duration,
            fps=24,
            aspect_ratio="16:9",
            status="pending"
        )

        self.db.add(db_gen)
        await self.db.commit()
        await self.db.refresh(db_gen)

        return VideoGenerationResponse.model_validate(db_gen)

    async def batch_generate_for_episode(self, episode_id: int) -> str:
        """
        为章节批量生成视频（所有分镜）

        Args:
            episode_id: 章节 ID

        Returns:
            任务 ID
        """
        # 验证章节存在
        episode_result = await self.db.execute(
            select(Episode).where(Episode.id == episode_id)
        )
        episode = episode_result.scalar_one_or_none()

        if not episode:
            raise EpisodeNotFoundException(episode_id)

        # 获取章节所有分镜
        storyboards_result = await self.db.execute(
            select(Storyboard).where(Storyboard.episode_id == episode_id)
        )
        storyboards = storyboards_result.scalars().all()

        # 获取这些分镜的图片生成
        storyboard_ids = [s.id for s in storyboards]
        image_gens_result = await self.db.execute(
            select(ImageGeneration).where(
                ImageGeneration.storyboard_id.in_(storyboard_ids),
                ImageGeneration.status == "completed"
            )
        )
        image_gens = image_gens_result.scalars().all()

        # 创建异步任务
        import uuid
        task_id = str(uuid.uuid4())

        db_task = AsyncTask(
            id=task_id,
            type="batch_video_generation",
            status="pending",
            resource_id=str(episode_id),
            message=f"开始批量生成 {len(image_gens)} 个视频..."
        )
        self.db.add(db_task)
        await self.db.commit()

        return task_id


# 后台任务处理函数
async def process_batch_video_generation(task_id: str, episode_id: int):
    """处理批量视频生成的后台任务"""
    from src.database import async_session_maker

    async with async_session_maker() as db:
        try:
            # 更新任务状态
            result = await db.execute(select(AsyncTask).where(AsyncTask.id == task_id))
            task = result.scalar_one_or_none()
            if task:
                task.status = "processing"
                task.progress = 10
                await db.commit()

            # 获取章节
            episode_result = await db.execute(
                select(Episode).where(Episode.id == episode_id)
            )
            episode = episode_result.scalar_one_or_none()
            if not episode:
                raise Exception("Episode not found")

            # 获取章节所有分镜
            storyboards_result = await db.execute(
                select(Storyboard).where(Storyboard.episode_id == episode_id)
            )
            storyboards = storyboards_result.scalars().all()

            # 获取这些分镜的图片生成
            storyboard_ids = [s.id for s in storyboards]
            image_gens_result = await db.execute(
                select(ImageGeneration).where(
                    ImageGeneration.storyboard_id.in_(storyboard_ids),
                    ImageGeneration.status == "completed"
                )
            )
            image_gens = image_gens_result.scalars().all()

            # 创建视频生成任务
            created_count = 0
            for image_gen in image_gens:
                # 检查是否已存在视频生成
                existing_result = await db.execute(
                    select(VideoGeneration).where(
                        VideoGeneration.image_gen_id == image_gen.id
                    )
                )
                existing = existing_result.scalar_one_or_none()

                if not existing:
                    db_gen = VideoGeneration(
                        drama_id=episode.drama_id,
                        storyboard_id=image_gen.storyboard_id,
                        image_gen_id=image_gen.id,
                        provider="doubao",
                        prompt=f"Video for storyboard {image_gen.storyboard_id}",
                        model="default",
                        reference_mode="image",
                        image_url=image_gen.image_url,
                        first_frame_url=image_gen.image_url,
                        duration=5,
                        fps=24,
                        aspect_ratio="16:9",
                        status="pending"
                    )
                    db.add(db_gen)
                    created_count += 1

            await db.commit()

            # 更新任务为完成
            if task:
                task.status = "completed"
                task.progress = 100
                task.message = f"成功创建 {created_count} 个视频生成任务"
                task.result = f'{{"total_storyboards": {len(storyboards)}, "total_images": {len(image_gens)}, "new_generations": {created_count}}}'
                await db.commit()

        except Exception as e:
            # 更新任务为失败
            result = await db.execute(select(AsyncTask).where(AsyncTask.id == task_id))
            task = result.scalar_one_or_none()
            if task:
                task.status = "failed"
                task.error = str(e)
                await db.commit()
