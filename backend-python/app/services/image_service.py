from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any
from app.models.image_generation import ImageGeneration, ImageGenerationStatus
from app.models.drama import Drama
from app.services.ai_factory import get_ai_provider
from app.services.ai_base import ImageGenerationRequest, ImageGenerationResponse
from app.core.config import settings
from app.utils.logger import log
import os
import httpx
import uuid


class ImageGenerationService:
    """Service for handling image generation"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_image(
        self,
        drama_id: int,
        prompt: str,
        provider: str = "openai",
        model: str = "dall-e-3",
        size: str = "1024x1024",
        quality: str = "standard",
        style: Optional[str] = None,
        storyboard_id: Optional[int] = None,
        scene_id: Optional[int] = None,
        character_id: Optional[int] = None,
        image_type: str = "storyboard",
        frame_type: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        steps: Optional[int] = None,
        cfg_scale: Optional[float] = None,
        seed: Optional[int] = None,
        reference_images: Optional[list] = None
    ) -> ImageGeneration:
        """
        Generate an image using AI

        Args:
            drama_id: Drama ID
            prompt: Image generation prompt
            provider: AI provider name
            model: Model name
            size: Image size (e.g., "1024x1024")
            quality: Image quality
            style: Image style
            storyboard_id: Optional storyboard ID
            scene_id: Optional scene ID
            character_id: Optional character ID
            image_type: Type of image
            frame_type: Frame type for storyboard images
            negative_prompt: Negative prompt
            steps: Number of steps
            cfg_scale: CFG scale
            seed: Random seed
            reference_images: Reference image URLs

        Returns:
            ImageGeneration record
        """
        try:
            # Verify drama exists
            result = await self.db.execute(select(Drama).where(Drama.id == drama_id))
            drama = result.scalar_one_or_none()

            if not drama:
                raise ValueError(f"Drama with id {drama_id} not found")

            # Get AI config for provider
            from app.models.ai_config import AIServiceConfig
            config_result = await self.db.execute(
                select(AIServiceConfig)
                .where(
                    AIServiceConfig.service_type == "image",
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
            gen_request = ImageGenerationRequest(
                prompt=prompt,
                negative_prompt=negative_prompt,
                model=model,
                size=size,
                quality=quality,
                style=style,
                steps=steps,
                cfg_scale=cfg_scale,
                seed=seed,
                reference_images=reference_images
            )

            # Create image generation record
            image_gen = ImageGeneration(
                drama_id=drama_id,
                storyboard_id=storyboard_id,
                scene_id=scene_id,
                character_id=character_id,
                image_type=image_type,
                frame_type=frame_type,
                provider=provider,
                prompt=prompt,
                negative_prompt=negative_prompt,
                model=model,
                size=size,
                quality=quality,
                style=style,
                steps=steps,
                cfg_scale=cfg_scale,
                seed=seed,
                reference_images=reference_images,
                status=ImageGenerationStatus.PROCESSING.value
            )

            self.db.add(image_gen)
            await self.db.commit()
            await self.db.refresh(image_gen)

            # Generate image
            log.info(f"Generating image for drama {drama_id} using {provider}")
            response: ImageGenerationResponse = await ai_provider.generate_image(gen_request)

            # Update record with results
            if response.status == "completed":
                image_gen.image_url = response.image_url
                image_gen.local_path = response.local_path
                image_gen.width = response.width
                image_gen.height = response.height
                image_gen.status = ImageGenerationStatus.COMPLETED.value
                log.info(f"Image generated successfully: {image_gen.id}")
            else:
                image_gen.status = ImageGenerationStatus.FAILED.value
                image_gen.error_msg = response.error
                log.error(f"Image generation failed: {response.error}")

            await self.db.commit()
            await self.db.refresh(image_gen)

            return image_gen

        except Exception as e:
            log.error(f"Error generating image: {str(e)}")
            raise

    async def check_generation_status(self, generation_id: int) -> Dict[str, Any]:
        """
        Check status of image generation

        Args:
            generation_id: Image generation ID

        Returns:
            Status dict with keys: status, image_url, error
        """
        result = await self.db.execute(
            select(ImageGeneration).where(ImageGeneration.id == generation_id)
        )
        image_gen = result.scalar_one_or_none()

        if not image_gen:
            raise ValueError(f"Image generation {generation_id} not found")

        return {
            "status": image_gen.status,
            "image_url": image_gen.image_url,
            "local_path": image_gen.local_path,
            "error": image_gen.error_msg
        }
