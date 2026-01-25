import httpx
from typing import Dict, Any, List
import json
import os
from app.services.ai_base import (
    BaseAIProvider, BaseTextAIProvider,
    ImageGenerationRequest, ImageGenerationResponse,
    VideoGenerationRequest, VideoGenerationResponse,
    TextGenerationRequest, TextGenerationResponse
)
from app.core.config import settings
from app.utils.file import save_upload_file
import uuid


class OpenAIProvider(BaseAIProvider, BaseTextAIProvider):
    """OpenAI AI provider implementation"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )

    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """Generate image using DALL-E"""
        try:
            # Prepare request payload
            payload = {
                "model": request.model,
                "prompt": request.prompt,
                "n": 1,
                "size": request.size,
                "quality": request.quality
            }

            if request.style:
                payload["style"] = request.style

            # Call OpenAI API
            if self.endpoint:
                url = self.endpoint
            else:
                url = "/images/generations"

            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            # Extract image URL
            image_url = data["data"][0]["url"]
            revised_prompt = data["data"][0].get("revised_prompt")

            # Download and save image locally
            local_path = None
            width = None
            height = None

            try:
                # Download image
                async with httpx.AsyncClient() as download_client:
                    img_response = await download_client.get(image_url)
                    img_response.raise_for_status()
                    image_data = img_response.content

                # Save locally
                filename = f"openai_{uuid.uuid4()}.png"
                local_path = os.path.join(settings.LOCAL_STORAGE_PATH, filename)

                with open(local_path, "wb") as f:
                    f.write(image_data)

                # Update URL to local
                image_url = f"{settings.BASE_URL}/{filename}"

                # Get image dimensions if possible
                size_parts = request.size.split("x")
                if len(size_parts) == 2:
                    width = int(size_parts[0])
                    height = int(size_parts[1])

            except Exception as e:
                print(f"Failed to save image locally: {e}")

            return ImageGenerationResponse(
                image_url=image_url,
                local_path=local_path,
                width=width,
                height=height,
                status="completed"
            )

        except httpx.HTTPStatusError as e:
            error_msg = f"OpenAI API error: {e.response.status_code} - {e.response.text}"
            return ImageGenerationResponse(
                image_url="",
                status="failed",
                error=error_msg
            )
        except Exception as e:
            return ImageGenerationResponse(
                image_url="",
                status="failed",
                error=f"Failed to generate image: {str(e)}"
            )

    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResponse:
        """Generate video using Sora (OpenAI)"""
        try:
            # Prepare request payload for Sora
            payload = {
                "model": request.model or "sora-1.0",
                "prompt": request.prompt,
            }

            if request.image_url:
                payload["image"] = request.image_url

            if request.duration:
                payload["duration"] = request.duration

            if request.aspect_ratio:
                payload["aspect_ratio"] = request.aspect_ratio

            # Call OpenAI Sora API
            url = self.endpoint or "/videos/generations"

            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            # Sora returns a task ID for async processing
            task_id = data.get("id")

            return VideoGenerationResponse(
                video_url="",
                task_id=task_id,
                status="processing"
            )

        except httpx.HTTPStatusError as e:
            error_msg = f"OpenAI Sora API error: {e.response.status_code} - {e.response.text}"
            return VideoGenerationResponse(
                video_url="",
                status="failed",
                error=error_msg
            )
        except Exception as e:
            return VideoGenerationResponse(
                video_url="",
                status="failed",
                error=f"Failed to generate video: {str(e)}"
            )

    async def check_task_status(self, task_id: str) -> Dict[str, Any]:
        """Check async task status"""
        try:
            if not self.query_endpoint:
                # Default query endpoint for Sora
                url = f"/videos/{task_id}"
            else:
                url = self.query_endpoint.format(taskId=task_id)

            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()

            status = data.get("status", "pending")
            video_url = data.get("output", {}).get("video_url", "")

            return {
                "status": "completed" if status == "succeeded" else status,
                "result": {"video_url": video_url} if video_url else None,
                "error": data.get("error") if status == "failed" else None
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }

    async def generate_text(self, request: TextGenerationRequest) -> TextGenerationResponse:
        """Generate text using GPT"""
        try:
            # Prepare request payload
            messages = []

            if request.system_prompt:
                messages.append({
                    "role": "system",
                    "content": request.system_prompt
                })

            messages.append({
                "role": "user",
                "content": request.prompt
            })

            payload = {
                "model": request.model,
                "messages": messages,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature
            }

            # Call OpenAI API
            url = self.endpoint or "/chat/completions"

            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            # Extract generated text
            text = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})

            return TextGenerationResponse(
                text=text,
                usage=usage
            )

        except Exception as e:
            return TextGenerationResponse(
                text="",
                error=f"Failed to generate text: {str(e)}"
            )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
