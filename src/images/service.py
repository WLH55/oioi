"""
Images 模块业务逻辑层
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import BusinessValidationException
from src.core.schemas import PageResponse

from src.images.models import ImageGeneration
from src.dramas.models import Drama
from src.scenes.models import Scene
from src.storyboards.models import Storyboard

from .exceptions import (
    EpisodeNotFoundException,
    ImageGenerationNotFoundException,
    SceneNotFoundException,
)
from .schemas import (
    BackgroundImageResponse,
    ImageGenerationCreate,
    ImageGenerationResponse,
    ImageListResponse,
)


class ImageGenerationService:
    """图片生成服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_generations(
        self,
        page: int = 1,
        page_size: int = 20,
        drama_id: int | None = None,
        scene_id: int | None = None,
        storyboard_id: int | None = None,
        frame_type: str | None = None,
        status_filter: str | None = None
    ) -> PageResponse[list[ImageListResponse]]:
        """
        获取图片生成列表

        Args:
            page: 页码
            page_size: 每页大小
            drama_id: 剧目 ID 过滤
            scene_id: 场景 ID 过滤
            storyboard_id: 分镜 ID 过滤
            frame_type: 帧类型过滤
            status_filter: 状态过滤

        Returns:
            分页响应
        """
        query = select(ImageGeneration)

        # 应用过滤条件
        if drama_id:
            query = query.where(ImageGeneration.drama_id == drama_id)
        if scene_id:
            query = query.where(ImageGeneration.scene_id == scene_id)
        if storyboard_id:
            query = query.where(ImageGeneration.storyboard_id == storyboard_id)
        if frame_type:
            query = query.where(ImageGeneration.frame_type == frame_type)
        if status_filter:
            query = query.where(ImageGeneration.status == status_filter)

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # 获取分页结果
        skip = (page - 1) * page_size
        query = query.offset(skip).limit(page_size).order_by(ImageGeneration.created_at.desc())
        result = await self.db.execute(query)
        generations = result.scalars().all()

        # 转换为响应模型
        items = [
            ImageListResponse(
                id=gen.id,
                storyboard_id=gen.storyboard_id,
                drama_id=gen.drama_id,
                scene_id=gen.scene_id,
                character_id=gen.character_id,
                image_type=gen.image_type,
                frame_type=gen.frame_type,
                provider=gen.provider,
                prompt=gen.prompt,
                model=gen.model,
                size=gen.size,
                quality=gen.quality,
                style=gen.style,
                steps=gen.steps,
                cfg_scale=gen.cfg_scale,
                seed=gen.seed,
                image_url=gen.image_url,
                local_path=gen.local_path,
                status=gen.status,
                error_msg=gen.error_msg,
                width=gen.width,
                height=gen.height,
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
        request: ImageGenerationCreate
    ) -> ImageGenerationResponse:
        """
        创建图片生成任务

        Args:
            request: 创建请求

        Returns:
            创建的图片生成记录
        """
        # 验证剧目存在
        result = await self.db.execute(
            select(Drama).where(Drama.id == int(request.drama_id))
        )
        drama = result.scalar_one_or_none()
        if not drama:
            raise BusinessValidationException(f"剧目不存在 (ID: {request.drama_id})")

        # 创建图片生成记录
        db_gen = ImageGeneration(
            drama_id=int(request.drama_id),
            storyboard_id=request.storyboard_id,
            scene_id=request.scene_id,
            character_id=request.character_id,
            image_type=request.image_type or "storyboard",
            frame_type=request.frame_type,
            provider=request.provider,
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            model=request.model,
            size=request.size,
            quality=request.quality,
            style=request.style,
            steps=request.steps,
            cfg_scale=request.cfg_scale,
            seed=request.seed,
            width=request.width,
            height=request.height,
            reference_images=request.reference_images,
            status=ImageGenerationStatus.PENDING.value
        )

        self.db.add(db_gen)
        await self.db.commit()
        await self.db.refresh(db_gen)

        return ImageGenerationResponse.model_validate(db_gen)

    async def get_generation(self, gen_id: int) -> ImageGenerationResponse:
        """
        获取图片生成详情

        Args:
            gen_id: 图片生成 ID

        Returns:
            图片生成详情
        """
        result = await self.db.execute(
            select(ImageGeneration).where(ImageGeneration.id == gen_id)
        )
        gen = result.scalar_one_or_none()

        if not gen:
            raise ImageGenerationNotFoundException(gen_id)

        return ImageGenerationResponse.model_validate(gen)

    async def delete_generation(self, gen_id: int) -> None:
        """
        删除图片生成记录

        Args:
            gen_id: 图片生成 ID
        """
        result = await self.db.execute(
            select(ImageGeneration).where(ImageGeneration.id == gen_id)
        )
        gen = result.scalar_one_or_none()

        if not gen:
            raise ImageGenerationNotFoundException(gen_id)

        await self.db.delete(gen)
        await self.db.commit()

    async def generate_for_scene(self, scene_id: int) -> ImageGenerationResponse:
        """
        为场景生成图片

        Args:
            scene_id: 场景 ID

        Returns:
            创建的图片生成记录
        """
        # 验证场景存在
        result = await self.db.execute(select(Scene).where(Scene.id == scene_id))
        scene = result.scalar_one_or_none()

        if not scene:
            raise SceneNotFoundException(scene_id)

        # 创建图片生成记录
        db_gen = ImageGeneration(
            drama_id=scene.drama_id,
            scene_id=scene.id,
            image_type="scene",
            provider="openai",
            prompt=scene.prompt,
            model="dall-e-3",
            size="1024x1024",
            quality="standard",
            status=ImageGenerationStatus.PENDING.value
        )

        self.db.add(db_gen)
        await self.db.commit()
        await self.db.refresh(db_gen)

        # 更新场景状态
        scene.status = "pending"
        await self.db.commit()

        return ImageGenerationResponse.model_validate(db_gen)

    async def get_backgrounds_for_episode(self, episode_id: int) -> list[BackgroundImageResponse]:
        """
        获取章节的场景背景图片

        Args:
            episode_id: 章节 ID

        Returns:
            背景图片列表
        """
        # 验证章节存在
        episode_result = await self.db.execute(
            select(Episode).where(Episode.id == episode_id)
        )
        episode = episode_result.scalar_one_or_none()

        if not episode:
            raise EpisodeNotFoundException(episode_id)

        # 获取章节场景的已生成图片
        result = await self.db.execute(
            select(ImageGeneration)
            .where(
                ImageGeneration.drama_id == episode.drama_id,
                ImageGeneration.image_type == "scene",
                ImageGeneration.status == ImageGenerationStatus.COMPLETED.value
            )
            .order_by(ImageGeneration.created_at.desc())
        )

        image_gens = result.scalars().all()

        backgrounds = []
        for gen in image_gens:
            if gen.scene_id:
                scene_result = await self.db.execute(
                    select(Scene).where(Scene.id == gen.scene_id)
                )
                scene = scene_result.scalar_one_or_none()
                if scene and scene.episode_id == episode_id:
                    backgrounds.append(BackgroundImageResponse(
                        scene_id=scene.id,
                        location=scene.location,
                        time=scene.time,
                        image_url=gen.image_url,
                        local_path=gen.local_path,
                        image_gen_id=gen.id
                    ))

        return backgrounds

    async def extract_backgrounds_for_episode(
        self,
        episode_id: int,
        model: str | None = None
    ) -> str:
        """
        为章节提取场景背景（创建批量任务）

        Args:
            episode_id: 章节 ID
            model: 可选的模型名称

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

        # 获取章节所有场景
        scenes_result = await self.db.execute(
            select(Scene).where(Scene.episode_id == episode_id)
        )
        scenes_result.scalars().all()

        # 创建异步任务
        import uuid
        task_id = str(uuid.uuid4())

        db_task = AsyncTask(
            id=task_id,
            type="background_extraction",
            status="pending",
            resource_id=str(episode_id),
            message="开始提取场景..."
        )
        self.db.add(db_task)
        await self.db.commit()

        return task_id

    async def batch_generate_for_episode(self, episode_id: int) -> str:
        """
        为章节批量生成图片（所有分镜）

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

        # 创建异步任务
        import uuid
        task_id = str(uuid.uuid4())

        db_task = AsyncTask(
            id=task_id,
            type="batch_image_generation",
            status="pending",
            resource_id=str(episode_id),
            message=f"开始批量生成 {len(storyboards)} 个分镜图片..."
        )
        self.db.add(db_task)
        await self.db.commit()

        return task_id


# 后台任务处理函数
async def process_background_extraction(task_id: str, episode_id: int, model: str):
    """处理背景提取的后台任务"""
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

            # 获取章节所有场景
            scenes_result = await db.execute(
                select(Scene).where(Scene.episode_id == episode_id)
            )
            scenes = scenes_result.scalars().all()

            # 为每个场景创建图片生成任务
            created_count = 0
            for scene in scenes:
                # 检查是否已存在图片生成
                existing_result = await db.execute(
                    select(ImageGeneration).where(
                        ImageGeneration.scene_id == scene.id,
                        ImageGeneration.image_type == "scene"
                    )
                )
                existing = existing_result.scalar_one_or_none()

                if not existing:
                    db_gen = ImageGeneration(
                        drama_id=scene.drama_id,
                        scene_id=scene.id,
                        image_type="scene",
                        provider="openai",
                        prompt=scene.prompt,
                        model=model or "dall-e-3",
                        size="1024x1024",
                        quality="standard",
                        status=ImageGenerationStatus.PENDING.value
                    )
                    db.add(db_gen)
                    created_count += 1

            await db.commit()

            # 更新任务为完成
            if task:
                task.status = "completed"
                task.progress = 100
                task.message = f"成功提取 {created_count} 个场景"
                task.result = f'{{"total_scenes": {len(scenes)}, "new_generations": {created_count}}}'
                await db.commit()

        except Exception as e:
            # 更新任务为失败
            result = await db.execute(select(AsyncTask).where(AsyncTask.id == task_id))
            task = result.scalar_one_or_none()
            if task:
                task.status = "failed"
                task.error = str(e)
                await db.commit()


async def process_batch_image_generation(task_id: str, episode_id: int):
    """处理批量图片生成的后台任务"""
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

            # 获取章节所有分镜
            storyboards_result = await db.execute(
                select(Storyboard).where(Storyboard.episode_id == episode_id)
            )
            storyboards = storyboards_result.scalars().all()

            # 为每个分镜创建图片生成任务
            created_count = 0
            for storyboard in storyboards:
                existing_result = await db.execute(
                    select(ImageGeneration).where(
                        ImageGeneration.storyboard_id == storyboard.id,
                        ImageGeneration.image_type == "storyboard"
                    )
                )
                existing = existing_result.scalar_one_or_none()

                if not existing and storyboard.image_prompt:
                    db_gen = ImageGeneration(
                        drama_id=storyboard.drama_id,
                        storyboard_id=storyboard.id,
                        image_type="storyboard",
                        provider="openai",
                        prompt=storyboard.image_prompt,
                        model="dall-e-3",
                        size="1024x1792",
                        quality="standard",
                        status=ImageGenerationStatus.PENDING.value
                    )
                    db.add(db_gen)
                    created_count += 1

            await db.commit()

            # 更新任务为完成
            if task:
                task.status = "completed"
                task.progress = 100
                task.message = f"成功创建 {created_count} 个图片生成任务"
                task.result = f'{{"total_storyboards": {len(storyboards)}, "new_generations": {created_count}}}'
                await db.commit()

        except Exception as e:
            # 更新任务为失败
            result = await db.execute(select(AsyncTask).where(AsyncTask.id == task_id))
            task = result.scalar_one_or_none()
            if task:
                task.status = "failed"
                task.error = str(e)
                await db.commit()
