"""
Episodes 模块服务层

提供集数相关的业务逻辑处理
"""
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.episodes.models import Episode
from src.scenes.models import Scene
from src.storyboards.models import Storyboard

from .exceptions import EpisodeNotFound


class EpisodeService:
    """集数服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self,
        drama_id: int | None = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[list[Episode], int]:
        """
        获取集数列表

        Args:
            drama_id: 剧目ID，可选
            skip: 跳过数量
            limit: 限制数量

        Returns:
            (集数列表, 总数)
        """
        query = select(Episode)

        if drama_id is not None:
            query = query.where(Episode.drama_id == drama_id)

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # 获取分页数据
        query = query.offset(skip).limit(limit)
        query = query.order_by(Episode.episode_number)

        result = await self.db.execute(query)
        episodes = result.scalars().all()

        return list(episodes), total

    async def get_by_id(self, episode_id: int) -> Episode:
        """
        根据ID获取集数

        Args:
            episode_id: 集数ID

        Returns:
            Episode 对象

        Raises:
            EpisodeNotFound: 集数不存在
        """
        result = await self.db.execute(
            select(Episode)
            .options(selectinload(Episode.drama))
            .where(Episode.id == episode_id)
        )
        episode = result.scalar_one_or_none()

        if not episode:
            raise EpisodeNotFound(episode_id)

        return episode

    async def get_by_drama_and_number(
        self,
        drama_id: int,
        episode_number: int
    ) -> Episode | None:
        """
        根据剧目ID和集数编号获取集数

        Args:
            drama_id: 剧目ID
            episode_number: 集数编号

        Returns:
            Episode 对象或 None
        """
        result = await self.db.execute(
            select(Episode).where(
                Episode.drama_id == drama_id,
                Episode.episode_number == episode_number
            )
        )
        return result.scalar_one_or_none()

    async def create(self, drama_id: int, data: dict[str, Any]) -> Episode:
        """
        创建集数

        Args:
            drama_id: 剧目ID
            data: 集数数据

        Returns:
            创建的 Episode 对象
        """
        episode = Episode(
            drama_id=drama_id,
            episode_number=data.get("episode_number", 1),
            title=data.get("title", ""),
            description=data.get("description"),
            script_content=data.get("script_content"),
        )

        self.db.add(episode)
        await self.db.commit()
        await self.db.refresh(episode)

        return episode

    async def update(self, episode_id: int, data: dict[str, Any]) -> Episode:
        """
        更新集数

        Args:
            episode_id: 集数ID
            data: 更新数据

        Returns:
            更新后的 Episode 对象

        Raises:
            EpisodeNotFound: 集数不存在
        """
        episode = await self.get_by_id(episode_id)

        # 更新字段
        if "title" in data:
            episode.title = data["title"]
        if "description" in data:
            episode.description = data["description"]
        if "script_content" in data:
            episode.script_content = data["script_content"]
        if "duration" in data:
            episode.duration = data["duration"]
        if "status" in data:
            episode.status = data["status"]
        if "video_url" in data:
            episode.video_url = data["video_url"]
        if "thumbnail" in data:
            episode.thumbnail = data["thumbnail"]

        await self.db.commit()
        await self.db.refresh(episode)

        return episode

    async def delete(self, episode_id: int) -> None:
        """
        删除集数

        Args:
            episode_id: 集数ID

        Raises:
            EpisodeNotFound: 集数不存在
        """
        episode = await self.get_by_id(episode_id)
        await self.db.delete(episode)
        await self.db.commit()

    async def finalize(
        self,
        episode_id: int,
        timeline_data: dict[str, Any] | None = None
    ) -> str:
        """
        完成集数制作，准备视频合成

        Args:
            episode_id: 集数ID
            timeline_data: 时间线数据（可选）

        Returns:
            任务ID

        Raises:
            EpisodeNotFound: 集数不存在
        """
        episode = await self.get_by_id(episode_id)

        # 创建任务ID
        task_id = f"finalize_{episode_id}_{uuid.uuid4().hex[:8]}"

        # 更新状态为处理中
        episode.status = "processing"
        await self.db.commit()

        return task_id

    async def get_download_info(self, episode_id: int) -> dict[str, Any]:
        """
        获取集数下载信息

        Args:
            episode_id: 集数ID

        Returns:
            下载信息字典

        Raises:
            EpisodeNotFound: 集数不存在
            EpisodeNotFinalizable: 集数没有视频
        """
        episode = await self.get_by_id(episode_id)

        if not episode.video_url:
            from .exceptions import EpisodeHasNoVideo
            raise EpisodeHasNoVideo(episode_id)

        return {
            "video_url": episode.video_url,
            "title": episode.title,
            "episode_number": episode.episode_number,
            "duration": episode.duration,
            "status": episode.status
        }

    async def get_storyboards(self, episode_id: int) -> list[Storyboard]:
        """
        获取集数的所有分镜

        Args:
            episode_id: 集数ID

        Returns:
            Storyboard 列表
        """
        result = await self.db.execute(
            select(Storyboard)
            .where(Storyboard.episode_id == episode_id)
            .order_by(Storyboard.storyboard_number)
        )
        return list(result.scalars().all())

    async def get_scenes(self, episode_id: int) -> list[Scene]:
        """
        获取集数的所有场景

        Args:
            episode_id: 集数ID

        Returns:
            Scene 列表
        """
        result = await self.db.execute(
            select(Scene)
            .where(Scene.episode_id == episode_id)
            .order_by(Scene.id)
        )
        return list(result.scalars().all())

    async def get_detail(self, episode_id: int) -> dict[str, Any]:
        """
        获取集数详情（包含关联数据统计）

        Args:
            episode_id: 集数ID

        Returns:
            详情字典
        """
        episode = await self.get_by_id(episode_id)

        # 获取分镜数量
        storyboard_count_result = await self.db.execute(
            select(func.count()).where(Storyboard.episode_id == episode_id)
        )
        storyboard_count = storyboard_count_result.scalar() or 0

        # 获取场景数量
        scene_count_result = await self.db.execute(
            select(func.count()).where(Scene.episode_id == episode_id)
        )
        scene_count = scene_count_result.scalar() or 0

        return {
            "id": episode.id,
            "drama_id": episode.drama_id,
            "drama_title": episode.drama.title if episode.drama else None,
            "episode_number": episode.episode_number,
            "title": episode.title,
            "description": episode.description,
            "script_content": episode.script_content,
            "duration": episode.duration,
            "status": episode.status,
            "video_url": episode.video_url,
            "thumbnail": episode.thumbnail,
            "storyboard_count": storyboard_count,
            "scene_count": scene_count,
            "created_at": episode.created_at,
            "updated_at": episode.updated_at,
        }
