"""
Script Generation Service

Handles AI-powered script and character generation for dramas.
"""

import json
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.drama import Drama, Episode, Character, Scene
from app.services.ai_factory import get_ai_provider
from app.services.task_service import TaskService
from app.utils.logger import log


class ScriptGenerationService:
    """Service for generating scripts and characters using AI"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_service = TaskService(db)

    async def generate_characters(
        self,
        drama_id: int,
        genre: Optional[str] = None,
        style: Optional[str] = None,
        num_characters: int = 3,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate characters for a drama using AI

        Args:
            drama_id: Drama ID
            genre: Genre of the drama
            style: Style of the drama
            num_characters: Number of characters to generate
            custom_prompt: Custom prompt for character generation

        Returns:
            Dict with generation result and task info
        """
        try:
            # Get drama
            result = await self.db.execute(select(Drama).where(Drama.id == drama_id))
            drama = result.scalar_one_or_none()

            if not drama:
                raise ValueError(f"Drama {drama_id} not found")

            # Build prompt for character generation
            prompt = self._build_character_generation_prompt(
                title=drama.title,
                genre=genre or drama.metadata.get("genre", "drama") if drama.metadata else "drama",
                style=style or drama.metadata.get("style", "realistic") if drama.metadata else "realistic",
                num_characters=num_characters,
                custom_prompt=custom_prompt
            )

            # Get AI provider
            ai_provider = get_ai_provider("openai", "text")

            # Generate characters
            response = await ai_provider.generate_text(
                prompt=prompt,
                model="gpt-4",
                max_tokens=2000,
                temperature=0.8
            )

            # Parse AI response
            characters_data = self._parse_character_response(response.text)

            # Save characters to database
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

            # Refresh to get IDs
            for char in saved_characters:
                await self.db.refresh(char)

            log.info(f"Generated {len(saved_characters)} characters for drama {drama_id}")

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

        except Exception as e:
            log.error(f"Error generating characters: {str(e)}")
            raise

    async def generate_script(
        self,
        drama_id: int,
        episode_num: int,
        plot_outline: str,
        style: Optional[str] = None,
        duration: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate script for an episode using AI

        Args:
            drama_id: Drama ID
            episode_num: Episode number
            plot_outline: Plot outline for the episode
            style: Script style
            duration: Target duration in minutes

        Returns:
            Dict with generation result and task info
        """
        try:
            # Get drama
            result = await self.db.execute(select(Drama).where(Drama.id == drama_id))
            drama = result.scalar_one_or_none()

            if not drama:
                raise ValueError(f"Drama {drama_id} not found")

            # Get existing characters
            char_result = await self.db.execute(
                select(Character).where(Character.drama_id == drama_id)
            )
            characters = char_result.scalars().all()

            # Build prompt for script generation
            prompt = self._build_script_generation_prompt(
                drama_title=drama.title,
                episode_num=episode_num,
                plot_outline=plot_outline,
                characters=[{
                    "name": c.name,
                    "role": c.role,
                    "description": c.description,
                    "personality": c.personality
                } for c in characters],
                style=style,
                duration=duration
            )

            # Get AI provider
            ai_provider = get_ai_provider("openai", "text")

            # Generate script
            response = await ai_provider.generate_text(
                prompt=prompt,
                model="gpt-4",
                max_tokens=4000,
                temperature=0.7
            )

            # Parse script
            script_data = self._parse_script_response(response.text)

            # Create or update episode
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

            log.info(f"Generated script for drama {drama_id}, episode {episode_num}")

            return {
                "drama_id": drama_id,
                "episode_id": episode.id,
                "episode_num": episode_num,
                "title": episode.title,
                "script_length": len(episode.script_content),
                "duration": episode.duration
            }

        except Exception as e:
            log.error(f"Error generating script: {str(e)}")
            raise

    async def generate_scenes_from_script(
        self,
        episode_id: int
    ) -> Dict[str, Any]:
        """
        Generate scene breakdowns from script

        Args:
            episode_id: Episode ID

        Returns:
            Dict with generated scenes
        """
        try:
            # Get episode
            result = await self.db.execute(select(Episode).where(Episode.id == episode_id))
            episode = result.scalar_one_or_none()

            if not episode:
                raise ValueError(f"Episode {episode_id} not found")

            if not episode.script_content:
                raise ValueError(f"Episode {episode_id} has no script content")

            # Build prompt for scene breakdown
            prompt = self._build_scene_breakdown_prompt(
                script=episode.script_content,
                episode_title=episode.title
            )

            # Get AI provider
            ai_provider = get_ai_provider("openai", "text")

            # Generate scene breakdown
            response = await ai_provider.generate_text(
                prompt=prompt,
                model="gpt-4",
                max_tokens=3000,
                temperature=0.6
            )

            # Parse scenes
            scenes_data = self._parse_scene_breakdown_response(response.text)

            # Delete existing scenes for this episode
            existing_scenes_result = await self.db.execute(
                select(Scene).where(Scene.episode_id == episode_id)
            )
            existing_scenes = existing_scenes_result.scalars().all()
            for scene in existing_scenes:
                await self.db.delete(scene)

            # Create new scenes
            saved_scenes = []
            for i, scene_data in enumerate(scenes_data):
                scene = Scene(
                    drama_id=episode.drama_id,
                    episode_id=episode_id,
                    scene_number=i + 1,
                    location=scene_data.get("location", "Unknown"),
                    time=scene_data.get("time", "Day"),
                    description=scene_data.get("description", ""),
                    prompt=scene_data.get("visual_prompt", ""),
                    duration=scene_data.get("duration", 0),
                    status="pending"
                )
                self.db.add(scene)
                saved_scenes.append(scene)

            await self.db.commit()

            log.info(f"Generated {len(saved_scenes)} scenes for episode {episode_id}")

            return {
                "episode_id": episode_id,
                "scenes_count": len(saved_scenes),
                "scenes": [
                    {
                        "scene_number": s.scene_number,
                        "location": s.location,
                        "time": s.time,
                        "description": s.description
                    }
                    for s in saved_scenes
                ]
            }

        except Exception as e:
            log.error(f"Error generating scenes: {str(e)}")
            raise

    def _build_character_generation_prompt(
        self,
        title: str,
        genre: str,
        style: str,
        num_characters: int,
        custom_prompt: Optional[str] = None
    ) -> str:
        """Build prompt for character generation"""
        base_prompt = f"""Generate {num_characters} unique and interesting characters for a {genre} drama titled "{title}".

Style: {style}

For each character, provide:
1. Name (Chinese name if style is Chinese)
2. Role (protagonist, antagonist, supporting, etc.)
3. Description (background, motivation, goals)
4. Appearance (physical features, clothing style)
5. Personality (key traits, behaviors)
6. Voice Style (for dubbing/voice acting)

Return the response in this JSON format:
[
  {{
    "name": "Character Name",
    "role": "protagonist|antagonist|supporting",
    "description": "Detailed background",
    "appearance": "Physical description",
    "personality": "Personality traits",
    "voice_style": "voice characteristics"
  }}
]

Make characters diverse, complex, and suitable for the {genre} genre."""

        if custom_prompt:
            base_prompt += f"\n\nAdditional requirements: {custom_prompt}"

        return base_prompt

    def _build_script_generation_prompt(
        self,
        drama_title: str,
        episode_num: int,
        plot_outline: str,
        characters: List[Dict[str, Any]],
        style: Optional[str] = None,
        duration: Optional[int] = None
    ) -> str:
        """Build prompt for script generation"""
        char_list = "\n".join([
            f"- {c['name']} ({c['role']}): {c['personality']}"
            for c in characters
        ])

        prompt = f"""Write a script for Episode {episode_num} of "{drama_title}".

Plot Outline:
{plot_outline}

Characters:
{char_list}

Style: {style or "Standard screenplay format"}
Target Duration: {duration or 20} minutes

Requirements:
1. Write in standard screenplay format
2. Include scene headings (location, time)
3. Include dialogue and action descriptions
4. Develop character personalities through dialogue
5. Include visual descriptions for key scenes
6. Create natural dialogue flow

Return the response in this JSON format:
{{
  "title": "Episode Title",
  "duration": estimated_minutes,
  "script": "Full script content here"
}}

Make the script engaging, well-paced, and true to the characters."""

        return prompt

    def _build_scene_breakdown_prompt(
        self,
        script: str,
        episode_title: str
    ) -> str:
        """Build prompt for scene breakdown"""
        return f"""Analyze the following script and break it down into individual scenes.

Episode: {episode_title}

Script:
{script}

For each scene, provide:
1. Scene number
2. Location (where the scene takes place)
3. Time (day/night/interior/exterior)
4. Description (brief summary of what happens)
5. Visual prompt (detailed description for image generation)
6. Duration (estimated in seconds)

Return the response in this JSON format:
[
  {{
    "location": "Location name",
    "time": "Day|Night|Interior|Exterior",
    "description": "Scene summary",
    "visual_prompt": "Detailed visual description for AI image generation",
    "duration": seconds
  }}
]"""

    def _parse_character_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse AI response for character generation"""
        try:
            # Try to parse as JSON
            # Find JSON array in response
            start = response.find("[")
            end = response.rfind("]") + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            log.warning(f"Failed to parse character response as JSON: {e}")

        # Fallback: return empty list
        return []

    def _parse_script_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response for script generation"""
        try:
            # Try to parse as JSON
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            log.warning(f"Failed to parse script response as JSON: {e}")

        # Fallback: return basic structure
        return {
            "title": "Generated Episode",
            "duration": 20,
            "script": response
        }

    def _parse_scene_breakdown_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse AI response for scene breakdown"""
        try:
            # Try to parse as JSON
            start = response.find("[")
            end = response.rfind("]") + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            log.warning(f"Failed to parse scene breakdown response as JSON: {e}")

        # Fallback: return empty list
        return []
