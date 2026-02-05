"""
剧目业务逻辑层

处理剧目的 CRUD 操作和业务逻辑。
"""
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dramas.models import Drama, Episode
from src.character_library.models import Character

from .exceptions import DramaNotFound
from .schemas import DramaCreate


class DramaService:
    """剧目服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Drama], int]:
        """
        获取剧目列表

        Args:
            skip: 跳过数量
            limit: 限制数量

        Returns:
            (剧目列表, 总数)
        """
        # 获取总数
        count_result = await self.db.execute(select(func.count(Drama.id)))
        total = count_result.scalar() or 0

        # 获取分页结果
        result = await self.db.execute(
            select(Drama)
            .offset(skip)
            .limit(limit)
            .order_by(Drama.created_at.desc())
        )
        dramas = result.scalars().all()

        return list(dramas), total

    async def get_by_id(self, drama_id: int) -> Drama:
        """
        根据 ID 获取剧目

        Args:
            drama_id: 剧目 ID

        Returns:
            剧目对象

        Raises:
            DramaNotFound: 剧目不存在
        """
        result = await self.db.execute(
            select(Drama).where(Drama.id == drama_id)
        )
        drama = result.scalar_one_or_none()

        if not drama:
            raise DramaNotFound(drama_id)

        return drama

    async def create(self, data: DramaCreate) -> Drama:
        """
        创建剧目

        Args:
            data: 创建数据

        Returns:
            创建的剧目对象
        """
        db_drama = Drama(**data.model_dump())
        self.db.add(db_drama)
        await self.db.commit()
        await self.db.refresh(db_drama)
        return db_drama

    async def update(self, drama_id: int, data: dict[str, Any]) -> Drama:
        """
        更新剧目

        Args:
            drama_id: 剧目 ID
            data: 更新数据

        Returns:
            更新后的剧目对象

        Raises:
            DramaNotFound: 剧目不存在
        """
        drama = await self.get_by_id(drama_id)

        # 更新字段
        for field, value in data.items():
            if hasattr(drama, field) and value is not None:
                setattr(drama, field, value)

        await self.db.commit()
        await self.db.refresh(drama)
        return drama

    async def delete(self, drama_id: int) -> None:
        """
        删除剧目

        Args:
            drama_id: 剧目 ID

        Raises:
            DramaNotFound: 剧目不存在
        """
        drama = await self.get_by_id(drama_id)
        await self.db.delete(drama)
        await self.db.commit()

    async def get_episodes(self, drama_id: int) -> list[Episode]:
        """
        获取剧目的所有集数

        Args:
            drama_id: 剧目 ID

        Returns:
            集数列表

        Raises:
            DramaNotFound: 剧目不存在
        """
        # 验证剧目存在
        await self.get_by_id(drama_id)

        result = await self.db.execute(
            select(Episode)
            .where(Episode.drama_id == drama_id)
            .order_by(Episode.episode_number)
        )
        return list(result.scalars().all())

    async def create_episode(
        self, drama_id: int, episode_data: dict[str, Any]
    ) -> Episode:
        """
        为剧目创建集数

        Args:
            drama_id: 剧目 ID
            episode_data: 集数数据

        Returns:
            创建的集数对象

        Raises:
            DramaNotFound: 剧目不存在
        """
        # 验证剧目存在
        await self.get_by_id(drama_id)

        db_episode = Episode(
            drama_id=drama_id,
            **episode_data
        )
        self.db.add(db_episode)
        await self.db.commit()
        await self.db.refresh(db_episode)
        return db_episode

    async def batch_save_episodes(
        self, drama_id: int, episodes_data: list[dict[str, Any]]
    ) -> int:
        """
        批量保存集数

        Args:
            drama_id: 剧目 ID
            episodes_data: 集数数据列表

        Returns:
            保存的集数数量

        Raises:
            DramaNotFound: 剧目不存在
        """
        # 验证剧目存在
        await self.get_by_id(drama_id)

        # 删除现有集数
        await self.db.execute(
            select(Episode).where(Episode.drama_id == drama_id)
        )

        # 创建新集数
        saved_count = 0
        for ep_data in episodes_data:
            db_episode = Episode(
                drama_id=drama_id,
                **ep_data
            )
            self.db.add(db_episode)
            saved_count += 1

        await self.db.commit()
        return saved_count

    async def get_characters(self, drama_id: int) -> list[Character]:
        """
        获取剧目的所有角色

        Args:
            drama_id: 剧目 ID

        Returns:
            角色列表

        Raises:
            DramaNotFound: 剧目不存在
        """
        # 验证剧目存在
        await self.get_by_id(drama_id)

        result = await self.db.execute(
            select(Character)
            .where(Character.drama_id == drama_id)
            .order_by(Character.sort_order)
        )
        return list(result.scalars().all())

    async def create_character(
        self, drama_id: int, character_data: dict[str, Any]
    ) -> Character:
        """
        为剧目创建角色

        Args:
            drama_id: 剧目 ID
            character_data: 角色数据

        Returns:
            创建的角色对象

        Raises:
            DramaNotFound: 剧目不存在
        """
        # 验证剧目存在
        await self.get_by_id(drama_id)

        db_character = Character(
            drama_id=drama_id,
            **character_data
        )
        self.db.add(db_character)
        await self.db.commit()
        await self.db.refresh(db_character)
        return db_character

    async def batch_save_characters(
        self, drama_id: int, characters_data: list[dict[str, Any]]
    ) -> int:
        """
        批量保存角色

        Args:
            drama_id: 剧目 ID
            characters_data: 角色数据列表

        Returns:
            保存的角色数量

        Raises:
            DramaNotFound: 剧目不存在
        """
        # 验证剧目存在
        await self.get_by_id(drama_id)

        # 删除现有角色
        await self.db.execute(
            select(Character).where(Character.drama_id == drama_id)
        )

        # 创建新角色
        saved_count = 0
        for char_data in characters_data:
            db_character = Character(
                drama_id=drama_id,
                **char_data
            )
            self.db.add(db_character)
            saved_count += 1

        await self.db.commit()
        return saved_count

    async def save_outline(self, drama_id: int, outline: dict[str, Any]) -> None:
        """
        保存剧目大纲

        Args:
            drama_id: 剧目 ID
            outline: 大纲数据

        Raises:
            DramaNotFound: 剧目不存在
        """
        drama = await self.get_by_id(drama_id)

        if drama.meta_data is None:
            drama.meta_data = {}

        drama.meta_data["outline"] = outline
        await self.db.commit()

    async def save_progress(
        self, drama_id: int, progress: dict[str, Any]
    ) -> Drama:
        """
        保存剧目进度

        Args:
            drama_id: 剧目 ID
            progress: 进度数据

        Returns:
            更新后的剧目对象

        Raises:
            DramaNotFound: 剧目不存在
        """
        drama = await self.get_by_id(drama_id)

        if drama.meta_data is None:
            drama.meta_data = {}

        drama.meta_data["progress"] = progress

        # 更新状态
        if "status" in progress:
            drama.status = progress["status"]

        await self.db.commit()
        await self.db.refresh(drama)
        return drama

    async def get_stats(self) -> dict[str, Any]:
        """
        获取剧目统计信息

        Returns:
            统计数据
        """
        # 统计总剧目数
        total_dramas_result = await self.db.execute(select(func.count(Drama.id)))
        total_dramas = total_dramas_result.scalar() or 0

        # 按状态统计剧目
        status_stats_result = await self.db.execute(
            select(Drama.status, func.count(Drama.id))
            .group_by(Drama.status)
        )
        status_stats = {row[0]: row[1] for row in status_stats_result.all()}

        # 统计总集数
        total_episodes_result = await self.db.execute(select(func.count(Episode.id)))
        total_episodes = total_episodes_result.scalar() or 0

        # 统计总角色数
        total_characters_result = await self.db.execute(select(func.count(Character.id)))
        total_characters = total_characters_result.scalar() or 0

        return {
            "total_dramas": total_dramas,
            "total_episodes": total_episodes,
            "total_characters": total_characters,
            "status_breakdown": status_stats,
            "completed_dramas": status_stats.get("completed", 0),
            "in_progress": status_stats.get("producing", 0) + status_stats.get("draft", 0)
        }
