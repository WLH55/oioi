from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any
from app.models.video_generation import VideoGeneration, VideoStatus
from app.models.drama import Drama
from app.models.image_generation import ImageGeneration
from app.services.ai_factory import get_ai_provider
from app.services.ai_base import VideoGenerationRequest, VideoGenerationResponse
from app.core.config import settings
from app.utils.logger import log
import json


class VideoGenerationService:
    """Service for handling video generation"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_video(
        self,
        drama_id: int,
        prompt: str,
        provider: str = "doubao",
        model: Optional[str] = None,
        storyboard_id: Optional[int] = None,
        image_gen_id: Optional[int] = None,
        reference_mode: Optional[str] = "single",
        image_url: Optional[str] = None,
        first_frame_url: Optional[str] = None,
        last_frame_url: Optional[str] = None,
        reference_image_urls: Optional[list] = None,
        duration: Optional[int] = 5,
        fps: Optional[int] = 30,
        aspect_ratio: Optional[str] = "16:9",
        style: Optional[str] = None,
        motion_level: Optional[int] = None,
        camera_motion: Optional[str] = None,
        seed: Optional[int] = None
    ) -> VideoGeneration:
        """
        Generate a video using AI

        Args:
            drama_id: Drama ID
            prompt: Video generation prompt
            provider: AI provider name
            model: Model name
            storyboard_id: Optional storyboard ID
            image_gen_id: Optional image generation ID
            reference_mode: Reference mode (single, first_last, multiple, none)
            image_url: Image URL for single reference mode
            first_frame_url: First frame URL
            last_frame_url: Last frame URL
            reference_image_urls: Multiple reference image URLs
            duration: Video duration in seconds
            fps: Frames per second
            aspect_ratio: Aspect ratio (e.g., "16:9")
            style: Video style
            motion_level: Motion level (1-10)
            camera_motion: Camera motion type
            seed: Random seed

        Returns:
            VideoGeneration record
        """
        try:
            # Verify drama exists
            result = await self.db.execute(select(Drama).where(Drama.id == drama_id))
            drama = result.scalar_one_or_none()

            if not drama:
                raise ValueError(f"Drama with id {drama_id} not found")

            # Verify image_gen if provided
            if image_gen_id:
                result = await self.db.execute(
                    select(ImageGeneration).where(ImageGeneration.id == image_gen_id)
                )
                image_gen = result.scalar_one_or_none()

                if not image_gen:
                    raise ValueError(f"Image generation {image_gen_id} not found")

                # Use image from image_gen if no explicit image_url
                if not image_url and image_gen.image_url:
                    image_url = image_gen.image_url

            # Get AI config for provider
            from app.models.ai_config import AIServiceConfig
            config_result = await self.db.execute(
                select(AIServiceConfig)
                .where(
                    AIServiceConfig.service_type == "video",
                    AIServiceConfig.provider == provider,
                    AIServiceConfig.is_active == True
                )
                .order_by(AIServiceConfig.priority.desc())
                .limit(1)
            )
            ai_config = config_result.scalar_one_or_none()

            if not ai_config:
                raise ValueError(f"No active AI configuration found for provider: {provider}")

            # Prepare AI provider config
            provider_config = {
                "api_key": ai_config.api_key,
                "base_url": ai_config.base_url,
                "model": ai_config.model,
                "endpoint": ai_config.endpoint,
                "query_endpoint": ai_config.query_endpoint,
                "settings": ai_config.settings
            }

            # Create AI provider instance
            ai_provider = get_ai_provider(provider, provider_config)

            # Prepare generation request
            gen_request = VideoGenerationRequest(
                prompt=prompt,
                model=model,
                image_url=image_url,
                first_frame_url=first_frame_url,
                last_frame_url=last_frame_url,
                reference_mode=reference_mode,
                duration=duration,
                fps=fps,
                aspect_ratio=aspect_ratio,
                style=style,
                motion_level=motion_level,
                camera_motion=camera_motion,
                seed=seed
            )

            # Create video generation record
            video_gen = VideoGeneration(
                drama_id=drama_id,
                storyboard_id=storyboard_id,
                image_gen_id=image_gen_id,
                provider=provider,
                prompt=prompt,
                model=model,
                reference_mode=reference_mode,
                image_url=image_url,
                first_frame_url=first_frame_url,
                last_frame_url=last_frame_url,
                reference_image_urls=json.dumps(reference_image_urls) if reference_image_urls else None,
                duration=duration,
                fps=fps,
                aspect_ratio=aspect_ratio,
                style=style,
                motion_level=motion_level,
                camera_motion=camera_motion,
                seed=seed,
                status=VideoStatus.PROCESSING.value
            )

            self.db.add(video_gen)
            await self.db.commit()
            await self.db.refresh(video_gen)

            # Generate video
            log.info(f"Generating video for drama {drama_id} using {provider}")
            response: VideoGenerationResponse = await ai_provider.generate_video(gen_request)

            # Update record with results
            if response.task_id:
                # Async generation
                video_gen.task_id = response.task_id
                video_gen.status = VideoStatus.PROCESSING.value
                log.info(f"Video generation task started: {response.task_id}")
            elif response.status == "completed":
                # Sync generation (completed immediately)
                video_gen.video_url = response.video_url
                video_gen.local_path = response.local_path
                video_gen.width = response.width
                video_gen.height = response.height
                video_gen.duration = response.duration
                video_gen.status = VideoStatus.COMPLETED.value
                log.info(f"Video generated successfully: {video_gen.id}")
            else:
                video_gen.status = VideoStatus.FAILED.value
                video_gen.error_msg = response.error
                log.error(f"Video generation failed: {response.error}")

            await self.db.commit()
            await self.db.refresh(video_gen)

            return video_gen

        except Exception as e:
            log.error(f"Error generating video: {str(e)}")
            raise

    async def check_generation_status(self, generation_id: int) -> Dict[str, Any]:
        """
        Check status of video generation

        Args:
            generation_id: Video generation ID

        Returns:
            Status dict with keys: status, video_url, error, progress
        """
        result = await self.db.execute(
            select(VideoGeneration).where(VideoGeneration.id == generation_id)
        )
        video_gen = result.scalar_one_or_none()

        if not video_gen:
            raise ValueError(f"Video generation {generation_id} not found")

        # If task_id exists and status is processing, check with provider
        if video_gen.task_id and video_gen.status == VideoStatus.PROCESSING.value:
            try:
                from app.models.ai_config import AIServiceConfig
                config_result = await self.db.execute(
                    select(AIServiceConfig)
                    .where(
                        AIServiceConfig.service_type == "video",
                        AIServiceConfig.provider == video_gen.provider,
                        AIServiceConfig.is_active == True
                    )
                    .limit(1)
                )
                ai_config = config_result.scalar_one_or_none()

                if ai_config:
                    provider_config = {
                        "api_key": ai_config.api_key,
                        "base_url": ai_config.base_url,
                        "endpoint": ai_config.endpoint,
                        "query_endpoint": ai_config.query_endpoint
                    }

                    ai_provider = get_ai_provider(video_gen.provider, provider_config)
                    task_status = await ai_provider.check_task_status(video_gen.task_id)

                    # Update based on task status
                    if task_status["status"] == "completed":
                        result = task_status.get("result", {})
                        video_gen.video_url = result.get("video_url", "")
                        video_gen.status = VideoStatus.COMPLETED.value
                        video_gen.duration = result.get("duration")
                        await self.db.commit()
                    elif task_status["status"] == "failed":
                        video_gen.status = VideoStatus.FAILED.value
                        video_gen.error_msg = task_status.get("error", "Generation failed")
                        await self.db.commit()

                    return {
                        "status": video_gen.status,
                        "video_url": video_gen.video_url,
                        "error": video_gen.error_msg,
                        "progress": task_status.get("progress", 0)
                    }

            except Exception as e:
                log.error(f"Error checking task status: {str(e)}")

        return {
            "status": video_gen.status,
            "video_url": video_gen.video_url,
            "local_path": video_gen.local_path,
            "error": video_gen.error_msg,
            "progress": 100 if video_gen.status == VideoStatus.COMPLETED.value else 0
        }
