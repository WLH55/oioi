"""
Frame Prompt Service

Handles AI-powered frame prompt generation for different frame types.
"""

import json
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.drama import Drama, Episode, Scene, Character
from app.models.frame_prompt import FramePrompt
from app.services.ai_factory import get_ai_provider
from app.utils.logger import log


class FramePromptService:
    """Service for generating frame prompts for different types"""

    # Frame types supported
    FRAME_TYPES = [
        "opening",      # Opening title/credits frame
        "scene_start",  # First frame of a scene
        "scene_end",    # Last frame of a scene
        "transition",   # Transition between scenes
        "keyframe"      # Key action/emotional moment
    ]

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_frame_prompt(
        self,
        drama_id: int,
        episode_id: Optional[int] = None,
        scene_id: Optional[int] = None,
        frame_type: str = "keyframe",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a frame prompt for AI image generation

        Args:
            drama_id: Drama ID
            episode_id: Episode ID (optional)
            scene_id: Scene ID (optional)
            frame_type: Type of frame (opening, scene_start, scene_end, transition, keyframe)
            context: Additional context for frame generation

        Returns:
            Generated frame prompt
        """
        try:
            # Validate frame type
            if frame_type not in self.FRAME_TYPES:
                raise ValueError(f"Invalid frame type: {frame_type}")

            # Get drama
            drama_result = await self.db.execute(select(Drama).where(Drama.id == drama_id))
            drama = drama_result.scalar_one_or_none()

            if not drama:
                raise ValueError(f"Drama {drama_id} not found")

            # Get scene if provided
            scene = None
            if scene_id:
                scene_result = await self.db.execute(select(Scene).where(Scene.id == scene_id))
                scene = scene_result.scalar_one_or_none()

            # Get characters for drama
            char_result = await self.db.execute(
                select(Character)
                .where(Character.drama_id == drama_id)
                .order_by(Character.sort_order)
                .limit(5)
            )
            characters = char_result.scalars().all()

            # Generate prompt based on frame type
            prompt_data = await self._generate_prompt_by_type(
                frame_type=frame_type,
                drama=drama,
                scene=scene,
                characters=characters,
                context=context or {}
            )

            # Save to database
            frame_prompt = FramePrompt(
                drama_id=drama_id,
                episode_id=episode_id,
                scene_id=scene_id,
                frame_type=frame_type,
                prompt=prompt_data["prompt"],
                negative_prompt=prompt_data.get("negative_prompt"),
                style=prompt_data.get("style", "cinematic"),
                composition=prompt_data.get("composition"),
                lighting=prompt_data.get("lighting"),
                mood=prompt_data.get("mood"),
                metadata=context
            )

            self.db.add(frame_prompt)
            await self.db.commit()
            await self.db.refresh(frame_prompt)

            log.info(f"Generated {frame_type} frame prompt for drama {drama_id}")

            return {
                "id": frame_prompt.id,
                "frame_type": frame_type,
                "prompt": frame_prompt.prompt,
                "negative_prompt": frame_prompt.negative_prompt,
                "style": frame_prompt.style,
                "composition": frame_prompt.composition,
                "lighting": frame_prompt.lighting,
                "mood": frame_prompt.mood
            }

        except Exception as e:
            log.error(f"Error generating frame prompt: {str(e)}")
            raise

    async def generate_batch_frame_prompts(
        self,
        drama_id: int,
        episode_id: int,
        frame_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate multiple frame prompts for an episode

        Args:
            drama_id: Drama ID
            episode_id: Episode ID
            frame_types: List of frame types to generate (default: all)

        Returns:
            Generated frame prompts
        """
        try:
            if frame_types is None:
                frame_types = self.FRAME_TYPES

            # Get episode scenes
            scenes_result = await self.db.execute(
                select(Scene)
                .where(Scene.episode_id == episode_id)
                .order_by(Scene.scene_number)
            )
            scenes = scenes_result.scalars().all()

            generated_prompts = []

            # Generate opening frame
            if "opening" in frame_types:
                opening = await self.generate_frame_prompt(
                    drama_id=drama_id,
                    episode_id=episode_id,
                    frame_type="opening"
                )
                generated_prompts.append(opening)

            # Generate scene_start and scene_end for each scene
            for scene in scenes:
                if "scene_start" in frame_types:
                    start_prompt = await self.generate_frame_prompt(
                        drama_id=drama_id,
                        episode_id=episode_id,
                        scene_id=scene.id,
                        frame_type="scene_start"
                    )
                    generated_prompts.append(start_prompt)

                if "scene_end" in frame_types:
                    end_prompt = await self.generate_frame_prompt(
                        drama_id=drama_id,
                        episode_id=episode_id,
                        scene_id=scene.id,
                        frame_type="scene_end"
                    )
                    generated_prompts.append(end_prompt)

                if "keyframe" in frame_types:
                    # Generate 1-2 keyframes per scene
                    for i in range(2):
                        keyframe = await self.generate_frame_prompt(
                            drama_id=drama_id,
                            episode_id=episode_id,
                            scene_id=scene.id,
                            frame_type="keyframe",
                            context={"keyframe_index": i}
                        )
                        generated_prompts.append(keyframe)

            # Generate transitions between scenes
            if "transition" in frame_types and len(scenes) > 1:
                for i in range(len(scenes) - 1):
                    transition = await self.generate_frame_prompt(
                        drama_id=drama_id,
                        episode_id=episode_id,
                        frame_type="transition",
                        context={
                            "from_scene": scenes[i].id,
                            "to_scene": scenes[i + 1].id
                        }
                    )
                    generated_prompts.append(transition)

            log.info(f"Generated {len(generated_prompts)} frame prompts for episode {episode_id}")

            return {
                "episode_id": episode_id,
                "total_prompts": len(generated_prompts),
                "prompts": generated_prompts
            }

        except Exception as e:
            log.error(f"Error generating batch frame prompts: {str(e)}")
            raise

    async def _generate_prompt_by_type(
        self,
        frame_type: str,
        drama: Drama,
        scene: Optional[Scene],
        characters: List[Character],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate prompt based on frame type"""

        if frame_type == "opening":
            return await self._generate_opening_prompt(drama, characters)

        elif frame_type == "scene_start":
            return await self._generate_scene_start_prompt(drama, scene, characters)

        elif frame_type == "scene_end":
            return await self._generate_scene_end_prompt(drama, scene, characters)

        elif frame_type == "transition":
            return await self._generate_transition_prompt(drama, context)

        elif frame_type == "keyframe":
            return await self._generate_keyframe_prompt(drama, scene, characters, context)

        else:
            return {
                "prompt": f"{frame_type} frame for {drama.title}",
                "style": "cinematic"
            }

    async def _generate_opening_prompt(
        self,
        drama: Drama,
        characters: List[Character]
    ) -> Dict[str, Any]:
        """Generate opening title frame prompt"""

        # Get main character
        main_char = next((c for c in characters if c.role == "protagonist"), None)
        char_desc = main_char.appearance if main_char else ""

        genre_style_map = {
            "action": "dynamic, energetic, intense",
            "romance": "warm, soft, emotional",
            "thriller": "dark, mysterious, tense",
            "comedy": "bright, colorful, lively",
            "drama": "cinematic, dramatic, moody"
        }

        style = genre_style_map.get(drama.genre, "cinematic, professional")

        prompt = f"""Opening title frame for {drama.title}

Genre: {drama.genre or 'Drama'}
Style: {style}

This is the opening title frame. Design it to:
- Establish the mood and tone of the series
- Be visually striking and memorable
- Include the title "{drama.title}" in elegant typography
- Set the visual style for the entire series

Visual Elements:
- Cinematic composition
- Professional lighting
- High production value
- {style} atmosphere
- Title text: "{drama.title}"
{"Main character hint: " + char_desc if char_desc else ""}

The image should be in 16:9 aspect ratio, suitable as a series opening."""

        return {
            "prompt": prompt,
            "negative_prompt": "blurry, low quality, amateur, text-heavy, cluttered",
            "style": "cinematic",
            "composition": "centered title, balanced",
            "lighting": "cinematic",
            "mood": drama.genre or "dramatic"
        }

    async def _generate_scene_start_prompt(
        self,
        drama: Drama,
        scene: Scene,
        characters: List[Character]
    ) -> Dict[str, Any]:
        """Generate scene start frame prompt"""

        time_mood_map = {
            "Day": "bright, natural",
            "Night": "dark, moody",
            "Dawn": "soft, golden",
            "Dusk": "warm, fading"
        }

        mood = time_mood_map.get(scene.time, "cinematic")

        prompt = f"""Opening frame for scene {scene.scene_number}

Location: {scene.location}
Time: {scene.time}
Scene Description: {scene.description}

This is the establishing shot that opens the scene. Design it to:
- Establish the location clearly
- Set the time of day through lighting
- Create the appropriate mood ({mood})
- Be visually interesting and cinematic

Visual Elements:
- Wide or establishing shot
- {mood} lighting
- Clear sense of location
- Atmospheric details
- Cinematic composition

The image should be in 16:9 aspect ratio, suitable as a scene opening."""

        return {
            "prompt": prompt,
            "negative_prompt": "close-up, faces, characters, cluttered",
            "style": "cinematic",
            "composition": "wide, establishing",
            "lighting": scene.time.lower(),
            "mood": mood
        }

    async def _generate_scene_end_prompt(
        self,
        drama: Drama,
        scene: Scene,
        characters: List[Character]
    ) -> Dict[str, Any]:
        """Generate scene end frame prompt"""

        prompt = f"""Closing frame for scene {scene.scene_number}

Location: {scene.location}
Time: {scene.time}
Scene Description: {scene.description}

This is the final shot that closes the scene. Design it to:
- Provide visual closure to the scene
- Leave a lasting impression
- Match the emotional tone of the scene
- Transition smoothly to the next scene

Visual Elements:
- Intentional composition
- Emotional resonance
- Cinematic framing
- Atmospheric depth
- Memorable visual

The image should be in 16:9 aspect ratio, suitable as a scene closing."""

        return {
            "prompt": prompt,
            "negative_prompt": "chaotic, busy, distracting",
            "style": "cinematic",
            "composition": "balanced, resolved",
            "lighting": scene.time.lower(),
            "mood": "contemplative"
        }

    async def _generate_transition_prompt(
        self,
        drama: Drama,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate transition frame prompt"""

        prompt = f"""Transition frame for {drama.title}

This is a visual transition between scenes. Design it to:
- Bridge two scenes smoothly
- Maintain visual continuity
- Create a moment of pause or reflection
- Support the narrative flow

Visual Elements:
- Soft, diffused focus
- Abstract or impressionistic elements
- Subtle motion blur
- Transitional colors
- Dreamlike quality

The image should be in 16:9 aspect ratio, suitable as a scene transition."""

        return {
            "prompt": prompt,
            "negative_prompt": "sharp, detailed, characters, text, objects",
            "style": "impressionistic",
            "composition": "soft, flowing",
            "lighting": "diffused",
            "mood": "transitional"
        }

    async def _generate_keyframe_prompt(
        self,
        drama: Drama,
        scene: Scene,
        characters: List[Character],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate keyframe prompt for important moment"""

        keyframe_index = context.get("keyframe_index", 0)

        prompt = f"""Keyframe for scene {scene.scene_number if scene else 'N/A'}

Location: {scene.location if scene else 'Various'}
Scene Description: {scene.description if scene else drama.description}

This is a key moment in the scene. Design it to:
- Capture the emotional peak or dramatic action
- Feature the main character(s)
- Be visually dynamic and engaging
- Tell a story through visuals

Visual Elements:
- Dynamic composition
- Emotional expression
- Action or drama
- Cinematic lighting
- Professional quality

The image should be in 16:9 aspect ratio, suitable as a key story moment."""

        return {
            "prompt": prompt,
            "negative_prompt": "static, boring, empty, low energy",
            "style": "cinematic",
            "composition": "dynamic",
            "lighting": "dramatic",
            "mood": "intense"
        }
