"""
Script Generation 模块服务层

提供剧本生成相关的业务逻辑处理
"""
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.dramas.models import Drama, Episode
from src.character_library.models import Character
from src.scenes.models import Scene

from .exceptions import ScriptGenerationError


class ScriptGenerationService:
    """剧本生成服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_characters(
        self,
        drama_id: int,
        genre: str | None = None,
        style: str | None = None,
        num_characters: int = 3,
        custom_prompt: str | None = None
    ) -> dict[str, Any]:
        """
        为剧目生成角色

        Args:
            drama_id: 剧目ID
            genre: 类型
            style: 风格
            num_characters: 角色数量
            custom_prompt: 自定义提示词

        Returns:
            生成结果字典
        """
        # 获取剧目
        drama = await self._get_drama(drama_id)

        # TODO: 实际实现中应调用 AI 服务
        # 这里使用占位符实现
        characters_data = self._generate_placeholder_characters(
            drama, genre, style, num_characters
        )

        # 保存角色到数据库
        saved_characters = []
        for i, char_data in enumerate(characters_data):
            character = Character(
                drama_id=drama_id,
                name=char_data.get("name", f"Character {i+1}"),
                role=char_data.get("role", "supporting"),
                description=char_data.get("description", ""),
                appearance=char_data.get("appearance", ""),
                personality=char_data.get("personality", ""),
                voice_style=char_data.get("voice_style", "neutral"),
                sort_order=i
            )
            self.db.add(character)
            saved_characters.append(character)

        await self.db.commit()

        # 刷新以获取ID
        for char in saved_characters:
            await self.db.refresh(char)

        return {
            "drama_id": drama_id,
            "characters": [
                {
                    "id": char.id,
                    "name": char.name,
                    "role": char.role,
                    "description": char.description,
                    "appearance": char.appearance,
                    "personality": char.personality
                }
                for char in saved_characters
            ],
            "count": len(saved_characters)
        }

    async def generate_script(
        self,
        drama_id: int,
        episode_num: int,
        plot_outline: str,
        style: str | None = None,
        duration: int | None = None
    ) -> dict[str, Any]:
        """
        为集数生成剧本

        Args:
            drama_id: 剧目ID
            episode_num: 集数编号
            plot_outline: 剧情大纲
            style: 风格
            duration: 目标时长

        Returns:
            生成结果字典
        """
        # 获取剧目
        drama = await self._get_drama(drama_id)

        # 获取现有角色
        char_result = await self.db.execute(
            select(Character).where(Character.drama_id == drama_id)
        )
        char_result.scalars().all()

        # TODO: 实际实现中应调用 AI 服务
        # 这里使用占位符实现
        script_data = self._generate_placeholder_script(
            drama, episode_num, plot_outline, style, duration
        )

        # 创建或更新集数
        episode_result = await self.db.execute(
            select(Episode).where(
                Episode.drama_id == drama_id,
                Episode.episode_number == episode_num
            )
        )
        episode = episode_result.scalar_one_or_none()

        if not episode:
            episode = Episode(
                drama_id=drama_id,
                episode_number=episode_num,
                title=script_data.get("title", f"Episode {episode_num}"),
                script_content=script_data.get("script", ""),
                description=plot_outline,
                duration=duration or script_data.get("duration", 0),
                status="draft"
            )
            self.db.add(episode)
        else:
            episode.title = script_data.get("title", episode.title)
            episode.script_content = script_data.get("script", episode.script_content)
            episode.description = plot_outline
            episode.duration = duration or episode.duration

        await self.db.commit()
        await self.db.refresh(episode)

        return {
            "drama_id": drama_id,
            "episode_id": episode.id,
            "episode_num": episode_num,
            "title": episode.title,
            "script_length": len(episode.script_content),
            "duration": episode.duration
        }

    async def generate_scenes_from_script(
        self,
        episode_id: int
    ) -> dict[str, Any]:
        """
        从剧本生成场景

        Args:
            episode_id: 集数ID

        Returns:
            生成结果字典
        """
        # 获取集数
        episode = await self._get_episode(episode_id)

        if not episode.script_content:
            raise ScriptGenerationError("集数没有剧本内容")

        # TODO: 实际实现中应调用 AI 服务
        # 这里使用占位符实现
        scenes_data = self._generate_placeholder_scenes(episode)

        # 删除现有场景
        existing_scenes_result = await self.db.execute(
            select(Scene).where(Scene.episode_id == episode_id)
        )
        existing_scenes = existing_scenes_result.scalars().all()
        for scene in existing_scenes:
            await self.db.delete(scene)

        # 创建新场景
        saved_scenes = []
        for _i, scene_data in enumerate(scenes_data):
            scene = Scene(
                drama_id=episode.drama_id,
                episode_id=episode_id,
                location=scene_data.get("location", "Unknown"),
                time=scene_data.get("time", "Day"),
                prompt=scene_data.get("visual_prompt", ""),
                storyboard_count=1,
                status="pending"
            )
            self.db.add(scene)
            saved_scenes.append(scene)

        await self.db.commit()

        return {
            "episode_id": episode_id,
            "scenes_count": len(saved_scenes),
            "scenes": [
                {
                    "scene_number": i + 1,
                    "location": s.location,
                    "time": s.time,
                    "description": s.prompt or ""
                }
                for i, s in enumerate(saved_scenes)
            ]
        }

    # ============================================================================
    # 辅助方法
    # ============================================================================

    async def _get_drama(self, drama_id: int) -> Drama:
        """获取剧目"""
        result = await self.db.execute(
            select(Drama).where(Drama.id == drama_id)
        )
        drama = result.scalar_one_or_none()
        if not drama:
            from src.dramas.exceptions import DramaNotFound
            raise DramaNotFound(drama_id)
        return drama

    async def _get_episode(self, episode_id: int) -> Episode:
        """获取集数"""
        result = await self.db.execute(
            select(Episode)
            .options(selectinload(Episode.drama))
            .where(Episode.id == episode_id)
        )
        episode = result.scalar_one_or_none()
        if not episode:
            from src.episodes.exceptions import EpisodeNotFound
            raise EpisodeNotFound(episode_id)
        return episode

    def _generate_placeholder_characters(
        self,
        drama: Drama,
        genre: str | None,
        style: str | None,
        num_characters: int
    ) -> list[dict[str, Any]]:
        """生成占位符角色数据"""
        characters = []
        for i in range(num_characters):
            characters.append({
                "name": f"角色{i+1}",
                "role": "主角" if i == 0 else "配角",
                "description": f"这是角色{i+1}的描述",
                "appearance": f"角色{i+1}的外貌",
                "personality": f"角色{i+1}的性格",
                "voice_style": "neutral"
            })
        return characters

    def _generate_placeholder_script(
        self,
        drama: Drama,
        episode_num: int,
        plot_outline: str,
        style: str | None,
        duration: int | None
    ) -> dict[str, Any]:
        """生成占位符剧本数据"""
        return {
            "title": f"第{episode_num}集",
            "duration": duration or 20,
            "script": f"# {drama.title} - 第{episode_num}集\n\n{plot_outline}\n\n[剧本内容占位符]"
        }

    def _generate_placeholder_scenes(
        self,
        episode: Episode
    ) -> list[dict[str, Any]]:
        """生成占位符场景数据"""
        scenes = []
        # 根据剧本内容简单划分场景
        lines = episode.script_content.split('\n')
        current_scene = 1

        for line in lines:
            if line.strip().startswith('#') or line.strip().startswith('['):
                scenes.append({
                    "location": f"场景{current_scene}",
                    "time": "Day",
                    "visual_prompt": line.strip(),
                    "duration": 30
                })
                current_scene += 1

        if not scenes:
            scenes.append({
                "location": "默认场景",
                "time": "Day",
                "visual_prompt": episode.description or "默认提示",
                "duration": 30
            })

        return scenes
