"""
Scenes 模块服务层

提供场景相关的业务逻辑处理
"""
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.scenes.models import Scene

from .exceptions import SceneNotFound


class SceneService:
    """场景服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self,
        drama_id: int | None = None,
        episode_id: int | None = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[list[Scene], int]:
        """
        获取场景列表

        Args:
            drama_id: 剧目ID，可选
            episode_id: 集数ID，可选
            skip: 跳过数量
            limit: 限制数量

        Returns:
            (场景列表, 总数)
        """
        query = select(Scene)

        if drama_id is not None:
            query = query.where(Scene.drama_id == drama_id)
        if episode_id is not None:
            query = query.where(Scene.episode_id == episode_id)

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # 获取分页数据
        query = query.offset(skip).limit(limit)
        query = query.order_by(Scene.id)

        result = await self.db.execute(query)
        scenes = result.scalars().all()

        return list(scenes), total

    async def get_by_id(self, scene_id: int) -> Scene:
        """
        根据ID获取场景

        Args:
            scene_id: 场景ID

        Returns:
            Scene 对象

        Raises:
            SceneNotFound: 场景不存在
        """
        result = await self.db.execute(
            select(Scene)
            .options(
                selectinload(Scene.drama),
                selectinload(Scene.episode)
            )
            .where(Scene.id == scene_id)
        )
        scene = result.scalar_one_or_none()

        if not scene:
            raise SceneNotFound(scene_id)

        return scene

    async def create(self, drama_id: int, data: dict[str, Any]) -> Scene:
        """
        创建场景

        Args:
            drama_id: 剧目ID
            data: 场景数据

        Returns:
            创建的 Scene 对象
        """
        scene = Scene(
            drama_id=drama_id,
            episode_id=data.get("episode_id"),
            location=data.get("location", ""),
            time=data.get("time", ""),
            prompt=data.get("prompt", ""),
            storyboard_count=data.get("storyboard_count", 1),
        )

        self.db.add(scene)
        await self.db.commit()
        await self.db.refresh(scene)

        return scene

    async def update(self, scene_id: int, data: dict[str, Any]) -> Scene:
        """
        更新场景

        Args:
            scene_id: 场景ID
            data: 更新数据

        Returns:
            更新后的 Scene 对象

        Raises:
            SceneNotFound: 场景不存在
        """
        scene = await self.get_by_id(scene_id)

        # 更新字段
        if "location" in data:
            scene.location = data["location"]
        if "time" in data:
            scene.time = data["time"]
        if "prompt" in data:
            scene.prompt = data["prompt"]
        if "storyboard_count" in data:
            scene.storyboard_count = data["storyboard_count"]
        if "image_url" in data:
            scene.image_url = data["image_url"]
        if "status" in data:
            scene.status = data["status"]

        await self.db.commit()
        await self.db.refresh(scene)

        return scene

    async def update_prompt(self, scene_id: int, prompt: str) -> Scene:
        """
        更新场景提示词

        Args:
            scene_id: 场景ID
            prompt: 新的提示词

        Returns:
            更新后的 Scene 对象

        Raises:
            SceneNotFound: 场景不存在
        """
        scene = await self.get_by_id(scene_id)
        scene.prompt = prompt
        await self.db.commit()
        await self.db.refresh(scene)
        return scene

    async def delete(self, scene_id: int) -> None:
        """
        删除场景

        Args:
            scene_id: 场景ID

        Raises:
            SceneNotFound: 场景不存在
        """
        scene = await self.get_by_id(scene_id)
        await self.db.delete(scene)
        await self.db.commit()

    async def generate_image(self, scene_id: int) -> str:
        """
        生成场景图片

        Args:
            scene_id: 场景ID

        Returns:
            任务ID

        Raises:
            SceneNotFound: 场景不存在
        """
        scene = await self.get_by_id(scene_id)

        # 更新状态为待处理
        scene.status = "pending"
        await self.db.commit()

        # 创建任务ID
        task_id = f"scene_img_gen_{scene_id}_{uuid.uuid4().hex[:8]}"

        # 在实际实现中，这里会触发 AI 图片生成任务
        # 目前只返回任务ID
        return task_id

    async def get_detail(self, scene_id: int) -> dict[str, Any]:
        """
        获取场景详情

        Args:
            scene_id: 场景ID

        Returns:
            详情字典
        """
        scene = await self.get_by_id(scene_id)

        return {
            "id": scene.id,
            "drama_id": scene.drama_id,
            "drama_title": scene.drama.title if scene.drama else None,
            "episode_id": scene.episode_id,
            "episode_title": scene.episode.title if scene.episode else None,
            "location": scene.location,
            "time": scene.time,
            "prompt": scene.prompt,
            "storyboard_count": scene.storyboard_count,
            "image_url": scene.image_url,
            "status": scene.status,
            "created_at": scene.created_at,
            "updated_at": scene.updated_at,
        }
