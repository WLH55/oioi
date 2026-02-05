"""
Storyboards 模块服务层

提供分镜管理相关的业务逻辑处理
"""
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.episodes.models import Episode
from src.storyboards.models import Storyboard

from .exceptions import FramePromptNotFound, StoryboardNotFound


class StoryboardService:
    """分镜服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self,
        episode_id: int | None = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[list[Storyboard], int]:
        """
        获取分镜列表

        Args:
            episode_id: 集数ID，可选
            skip: 跳过数量
            limit: 限制数量

        Returns:
            (分镜列表, 总数)
        """
        query = select(Storyboard)

        if episode_id is not None:
            query = query.where(Storyboard.episode_id == episode_id)

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # 获取分页数据
        query = query.offset(skip).limit(limit)
        query = query.order_by(Storyboard.storyboard_number)

        result = await self.db.execute(query)
        storyboards = result.scalars().all()

        return list(storyboards), total

    async def get_by_id(self, storyboard_id: int) -> Storyboard:
        """
        根据ID获取分镜

        Args:
            storyboard_id: 分镜ID

        Returns:
            Storyboard 对象

        Raises:
            StoryboardNotFound: 分镜不存在
        """
        result = await self.db.execute(
            select(Storyboard)
            .options(selectinload(Storyboard.episode))
            .where(Storyboard.id == storyboard_id)
        )
        storyboard = result.scalar_one_or_none()

        if not storyboard:
            raise StoryboardNotFound(storyboard_id)

        return storyboard

    async def get_by_episode(self, episode_id: int) -> list[Storyboard]:
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

    async def create(self, episode_id: int, data: dict[str, Any]) -> Storyboard:
        """
        创建分镜

        Args:
            episode_id: 集数ID
            data: 分镜数据

        Returns:
            创建的 Storyboard 对象
        """
        # 获取集数以获取 drama_id
        episode_result = await self.db.execute(
            select(Episode).where(Episode.id == episode_id)
        )
        episode = episode_result.scalar_one_or_none()

        if not episode:
            from src.episodes.exceptions import EpisodeNotFound
            raise EpisodeNotFound(episode_id)

        storyboard = Storyboard(
            drama_id=episode.drama_id,
            episode_id=episode_id,
            scene_id=data.get("scene_id"),
            storyboard_number=data.get("storyboard_number", 1),
            title=data.get("title"),
            location=data.get("location"),
            time=data.get("time"),
            shot_type=data.get("shot_type"),
            angle=data.get("angle"),
            movement=data.get("movement"),
            action=data.get("action"),
            result=data.get("result"),
            atmosphere=data.get("atmosphere"),
            dialogue=data.get("dialogue"),
            description=data.get("description"),
            duration=data.get("duration", 5),
            status="pending"
        )

        self.db.add(storyboard)
        await self.db.commit()
        await self.db.refresh(storyboard)

        return storyboard

    async def update(self, storyboard_id: int, data: dict[str, Any]) -> Storyboard:
        """
        更新分镜

        Args:
            storyboard_id: 分镜ID
            data: 更新数据

        Returns:
            更新后的 Storyboard 对象

        Raises:
            StoryboardNotFound: 分镜不存在
        """
        storyboard = await self.get_by_id(storyboard_id)

        # 更新字段
        if "title" in data:
            storyboard.title = data["title"]
        if "location" in data:
            storyboard.location = data["location"]
        if "time" in data:
            storyboard.time = data["time"]
        if "shot_type" in data:
            storyboard.shot_type = data["shot_type"]
        if "angle" in data:
            storyboard.angle = data["angle"]
        if "movement" in data:
            storyboard.movement = data["movement"]
        if "action" in data:
            storyboard.action = data["action"]
        if "result" in data:
            storyboard.result = data["result"]
        if "atmosphere" in data:
            storyboard.atmosphere = data["atmosphere"]
        if "image_prompt" in data:
            storyboard.image_prompt = data["image_prompt"]
        if "video_prompt" in data:
            storyboard.video_prompt = data["video_prompt"]
        if "bgm_prompt" in data:
            storyboard.bgm_prompt = data["bgm_prompt"]
        if "sound_effect" in data:
            storyboard.sound_effect = data["sound_effect"]
        if "dialogue" in data:
            storyboard.dialogue = data["dialogue"]
        if "description" in data:
            storyboard.description = data["description"]
        if "duration" in data:
            storyboard.duration = data["duration"]
        if "video_url" in data:
            storyboard.video_url = data["video_url"]
        if "status" in data:
            storyboard.status = data["status"]

        await self.db.commit()
        await self.db.refresh(storyboard)

        return storyboard

    async def delete(self, storyboard_id: int) -> None:
        """
        删除分镜

        Args:
            storyboard_id: 分镜ID

        Raises:
            StoryboardNotFound: 分镜不存在
        """
        storyboard = await self.get_by_id(storyboard_id)
        await self.db.delete(storyboard)
        await self.db.commit()

    async def generate_for_episode(self, episode_id: int) -> str:
        """
        为集数生成分镜

        Args:
            episode_id: 集数ID

        Returns:
            任务ID

        Raises:
            StoryboardNotFound: 集数不存在
        """
        # 验证集数存在
        episode_result = await self.db.execute(
            select(Episode).where(Episode.id == episode_id)
        )
        episode = episode_result.scalar_one_or_none()

        if not episode:
            from src.episodes.exceptions import EpisodeNotFound
            raise EpisodeNotFound(episode_id)

        # 创建任务ID
        task_id = f"storyboard_gen_{episode_id}_{uuid.uuid4().hex[:8]}"

        # TODO: 实际实现中应创建后台任务进行 AI 分镜生成
        return task_id

    # ============================================================================
    # 帧提示词相关方法
    # ============================================================================

    async def create_frame_prompt(
        self,
        storyboard_id: int,
        frame_type: str,
        prompt: str
    ) -> FramePrompt:
        """
        创建帧提示词

        Args:
            storyboard_id: 分镜ID
            frame_type: 帧类型
            prompt: 提示词

        Returns:
            创建的 FramePrompt 对象
        """
        # 验证分镜存在
        await self.get_by_id(storyboard_id)

        frame_prompt = FramePrompt(
            storyboard_id=storyboard_id,
            frame_type=frame_type,
            prompt=prompt,
            description=f"Generated {frame_type} frame prompt"
        )

        self.db.add(frame_prompt)
        await self.db.commit()
        await self.db.refresh(frame_prompt)

        return frame_prompt

    async def get_frame_prompts(self, storyboard_id: int) -> list[FramePrompt]:
        """
        获取分镜的所有帧提示词

        Args:
            storyboard_id: 分镜ID

        Returns:
            FramePrompt 列表
        """
        result = await self.db.execute(
            select(FramePrompt)
            .where(FramePrompt.storyboard_id == storyboard_id)
            .order_by(FramePrompt.id)
        )
        return list(result.scalars().all())

    async def get_frame_prompt_by_id(self, prompt_id: int) -> FramePrompt:
        """
        根据ID获取帧提示词

        Args:
            prompt_id: 帧提示词ID

        Returns:
            FramePrompt 对象

        Raises:
            FramePromptNotFound: 帧提示词不存在
        """
        result = await self.db.execute(
            select(FramePrompt).where(FramePrompt.id == prompt_id)
        )
        frame_prompt = result.scalar_one_or_none()

        if not frame_prompt:
            raise FramePromptNotFound(prompt_id)

        return frame_prompt

    async def delete_frame_prompt(self, prompt_id: int) -> None:
        """
        删除帧提示词

        Args:
            prompt_id: 帧提示词ID

        Raises:
            FramePromptNotFound: 帧提示词不存在
        """
        frame_prompt = await self.get_frame_prompt_by_id(prompt_id)
        await self.db.delete(frame_prompt)
        await self.db.commit()
