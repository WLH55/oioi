"""
Storyboard Generation Service

Handles AI-powered storyboard generation for drama episodes.
"""

import json
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.drama import Drama, Episode, Scene, Storyboard
from app.services.ai_factory import get_ai_provider
from app.services.task_service import TaskService
from app.utils.logger import log


class StoryboardGenerationService:
    """Service for generating storyboards using AI"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_service = TaskService(db)

    async def generate_storyboards_for_episode(
        self,
        episode_id: int,
        style: Optional[str] = None,
        aspect_ratio: str = "16:9",
        num_shots_per_scene: int = 3
    ) -> Dict[str, Any]:
        """
        Generate storyboards for all scenes in an episode

        Args:
            episode_id: Episode ID
            style: Visual style for storyboards
            aspect_ratio: Aspect ratio for storyboard images
            num_shots_per_scene: Number of storyboard shots per scene

        Returns:
            Dict with generation result
        """
        try:
            # Get episode
            episode_result = await self.db.execute(select(Episode).where(Episode.id == episode_id))
            episode = episode_result.scalar_one_or_none()

            if not episode:
                raise ValueError(f"Episode {episode_id} not found")

            # Get all scenes for episode
            scenes_result = await self.db.execute(
                select(Scene).where(Scene.episode_id == episode_id).order_by(Scene.scene_number)
            )
            scenes = scenes_result.scalars().all()

            if not scenes:
                raise ValueError(f"No scenes found for episode {episode_id}")

            # Get drama for context
            drama_result = await self.db.execute(select(Drama).where(Drama.id == episode.drama_id))
            drama = drama_result.scalar_one_or_none()

            # Delete existing storyboards for this episode
            existing_result = await self.db.execute(
                select(Storyboard).where(Storyboard.episode_id == episode_id)
            )
            existing_storyboards = existing_result.scalars().all()
            for sb in existing_storyboards:
                await self.db.delete(sb)

            # Generate storyboards for each scene
            generated_storyboards = []
            for scene in scenes:
                scene_storyboards = await self._generate_storyboards_for_scene(
                    scene=scene,
                    drama=drama,
                    style=style,
                    aspect_ratio=aspect_ratio,
                    num_shots=num_shots_per_scene
                )
                generated_storyboards.extend(scene_storyboards)

            await self.db.commit()

            log.info(f"Generated {len(generated_storyboards)} storyboards for episode {episode_id}")

            return {
                "episode_id": episode_id,
                "total_storyboards": len(generated_storyboards),
                "storyboards": [
                    {
                        "id": sb.id,
                        "scene_number": sb.scene_number,
                        "shot_number": sb.shot_number,
                        "description": sb.description,
                        "image_prompt": sb.image_prompt
                    }
                    for sb in generated_storyboards
                ]
            }

        except Exception as e:
            log.error(f"Error generating storyboards: {str(e)}")
            await self.db.rollback()
            raise

    async def regenerate_storyboard(
        self,
        storyboard_id: int,
        new_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Regenerate a specific storyboard with new parameters

        Args:
            storyboard_id: Storyboard ID
            new_description: New description/prompt

        Returns:
            Updated storyboard
        """
        try:
            # Get storyboard
            result = await self.db.execute(select(Storyboard).where(Storyboard.id == storyboard_id))
            storyboard = result.scalar_one_or_none()

            if not storyboard:
                raise ValueError(f"Storyboard {storyboard_id} not found")

            # Get related scene and drama
            scene_result = await self.db.execute(select(Scene).where(Scene.id == storyboard.scene_id))
            scene = scene_result.scalar_one_or_none()

            drama_result = await self.db.execute(select(Drama).where(Drama.id == storyboard.drama_id))
            drama = drama_result.scalar_one_or_none()

            # Generate new prompt
            if new_description:
                storyboard.description = new_description

            new_prompt = await self._generate_storyboard_prompt(
                drama=drama,
                scene=scene,
                shot_type=storyboard.shot_type or "medium",
                description=storyboard.description
            )

            storyboard.image_prompt = new_prompt
            storyboard.status = "pending"

            await self.db.commit()
            await self.db.refresh(storyboard)

            log.info(f"Regenerated storyboard {storyboard_id}")

            return {
                "id": storyboard.id,
                "scene_number": storyboard.scene_number,
                "shot_number": storyboard.shot_number,
                "description": storyboard.description,
                "image_prompt": storyboard.image_prompt,
                "status": storyboard.status
            }

        except Exception as e:
            log.error(f"Error regenerating storyboard: {str(e)}")
            await self.db.rollback()
            raise

    async def optimize_storyboards_for_flow(
        self,
        episode_id: int
    ) -> Dict[str, Any]:
        """
        Optimize storyboard sequence for better visual flow and continuity

        Args:
            episode_id: Episode ID

        Returns:
            Optimized storyboard sequence
        """
        try:
            # Get all storyboards for episode
            result = await self.db.execute(
                select(Storyboard)
                .where(Storyboard.episode_id == episode_id)
                .order_by(Storyboard.scene_number,Storyboard.shot_number)
            )
            storyboards = result.scalars().all()

            if not storyboards:
                raise ValueError(f"No storyboards found for episode {episode_id}")

            # Build prompt for flow optimization
            storyboard_list = [
                {
                    "scene_number": sb.scene_number,
                    "shot_number": sb.shot_number,
                    "shot_type": sb.shot_type,
                    "description": sb.description,
                    "camera_movement": sb.camera_movement
                }
                for sb in storyboards
            ]

            prompt = self._build_flow_optimization_prompt(storyboard_list)

            # Get AI provider
            ai_provider = get_ai_provider("openai", "text")

            # Generate optimization suggestions
            response = await ai_provider.generate_text(
                prompt=prompt,
                model="gpt-4",
                max_tokens=2000,
                temperature=0.5
            )

            # Parse and apply optimizations
            optimizations = self._parse_optimization_response(response.text)

            # Apply camera movement and shot type suggestions
            for i, sb in enumerate(storyboards):
                if i < len(optimizations):
                    opt = optimizations[i]
                    if opt.get("camera_movement"):
                        sb.camera_movement = opt["camera_movement"]
                    if opt.get("shot_type"):
                        sb.shot_type = opt["shot_type"]
                    if opt.get("transition"):
                        sb.transition = opt["transition"]

            await self.db.commit()

            log.info(f"Optimized {len(storyboards)} storyboards for episode {episode_id}")

            return {
                "episode_id": episode_id,
                "optimized_count": len(storyboards),
                "optimizations": optimizations
            }

        except Exception as e:
            log.error(f"Error optimizing storyboards: {str(e)}")
            await self.db.rollback()
            raise

    async def _generate_storyboards_for_scene(
        self,
        scene: Scene,
        drama: Drama,
        style: Optional[str],
        aspect_ratio: str,
        num_shots: int
    ) -> List[Storyboard]:
        """Generate storyboards for a single scene"""
        storyboards = []

        # Generate shot breakdown using AI
        shot_breakdown = await self._generate_shot_breakdown(
            drama=drama,
            scene=scene,
            num_shots=num_shots
        )

        for i, shot in enumerate(shot_breakdown):
            # Generate detailed prompt for each shot
            image_prompt = await self._generate_storyboard_prompt(
                drama=drama,
                scene=scene,
                shot_type=shot.get("type", "medium"),
                description=shot.get("description", ""),
                camera_movement=shot.get("camera_movement", "static")
            )

            storyboard = Storyboard(
                drama_id=drama.id,
                episode_id=scene.episode_id,
                scene_id=scene.id,
                scene_number=scene.scene_number,
                shot_number=i + 1,
                shot_type=shot.get("type", "medium"),
                description=shot.get("description", ""),
                image_prompt=image_prompt,
                camera_movement=shot.get("camera_movement", "static"),
                duration=shot.get("duration", 3),
                aspect_ratio=aspect_ratio,
                status="pending"
            )

            self.db.add(storyboard)
            storyboards.append(storyboard)

        return storyboards

    async def _generate_shot_breakdown(
        self,
        drama: Drama,
        scene: Scene,
        num_shots: int
    ) -> List[Dict[str, Any]]:
        """Generate shot breakdown for a scene using AI"""
        prompt = f"""Break down this scene into {num_shots} storyboard shots.

Drama: {drama.title}
Scene {scene.scene_number}: {scene.description}
Location: {scene.location}
Time: {scene.time}

For each shot, provide:
1. Shot type (wide, medium, close-up, extreme close-up, etc.)
2. Description of what's visible in frame
3. Camera movement (static, pan, tilt, zoom, dolly, etc.)
4. Duration in seconds

Return the response in this JSON format:
[
  {{
    "type": "wide|medium|close-up|etc",
    "description": "What's visible in the shot",
    "camera_movement": "static|pan|tilt|zoom|dolly",
    "duration": seconds
  }}
]

Create a visually interesting sequence that covers the scene effectively."""

        try:
            ai_provider = get_ai_provider("openai", "text")
            response = await ai_provider.generate_text(
                prompt=prompt,
                model="gpt-4",
                max_tokens=1000,
                temperature=0.7
            )

            # Parse response
            start = response.text.find("[")
            end = response.text.rfind("]") + 1
            if start != -1 and end > start:
                json_str = response.text[start:end]
                return json.loads(json_str)

        except Exception as e:
            log.warning(f"Failed to parse shot breakdown: {e}")

        # Fallback: return basic shots
        return [
            {
                "type": "wide",
                "description": scene.description,
                "camera_movement": "static",
                "duration": 3
            }
        ] * num_shots

    async def _generate_storyboard_prompt(
        self,
        drama: Drama,
        scene: Scene,
        shot_type: str,
        description: str,
        camera_movement: str = "static"
    ) -> str:
        """Generate detailed image prompt for storyboard"""

        # Get visual style from drama metadata
        visual_style = drama.meta_data.get("visual_style", "realistic") if drama.meta_data else "realistic"

        prompt = f"""Create a {shot_type} shot storyboard frame for a {drama.genre or 'drama'} series.

Scene Description: {scene.description}
Location: {scene.location}
Time: {scene.time}
Shot Type: {shot_type}
Camera Movement: {camera_movement}

Visual Style: {visual_style}
Art Style: Cinematic storyboard, professional quality, detailed

Frame Composition: {description}

Include:
- Appropriate camera angle for {shot_type} shot
- Clear subject focus
- Proper depth of field
- Cinematic lighting
- Atmosphere and mood appropriate for {scene.time}

The image should be in 16:9 aspect ratio and suitable as a production storyboard."""

        return prompt

    def _build_flow_optimization_prompt(
        self,
        storyboards: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for storyboard flow optimization"""
        storyboard_text = "\n".join([
            f"Scene {sb['scene_number']}, Shot {sb['shot_number']}: "
            f"{sb['shot_type']} - {sb['description']} "
            f"(Camera: {sb.get('camera_movement', 'static')})"
            for sb in storyboards
        ])

        return f"""Analyze this storyboard sequence and suggest improvements for visual flow and continuity.

Current Sequence:
{storyboard_text}

For each shot, suggest:
1. Optimal camera movement (if current needs improvement)
2. Shot type refinement (if needed)
3. Transition to next shot (cut, fade, dissolve, wipe, etc.)

Return the response in this JSON format:
[
  {{
    "shot_index": 0,
    "camera_movement": "suggested movement",
    "shot_type": "refined shot type",
    "transition": "cut|fade|dissolve|wipe"
  }}
]

Focus on:
- Visual continuity
- Pacing and rhythm
- Narrative clarity
- Cinematic quality"""

    def _parse_optimization_response(
        self,
        response: str
    ) -> List[Dict[str, Any]]:
        """Parse AI optimization response"""
        try:
            start = response.find("[")
            end = response.rfind("]") + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except Exception as e:
            log.warning(f"Failed to parse optimization response: {e}")

        return []
