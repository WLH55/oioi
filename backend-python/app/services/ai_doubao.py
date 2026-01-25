import httpx
from typing import Dict, Any
import json
import os
from app.services.ai_base import (
    BaseAIProvider,
    VideoGenerationRequest, VideoGenerationResponse
)
from app.core.config import settings
import uuid


class DoubaoProvider(BaseAIProvider):
    """Doubao (Volcengine) video generation provider"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=120.0
        )

    async def generate_image(self, request):
        """Doubao doesn't support image generation"""
        return {
            "status": "failed",
            "error": "Doubao provider doesn't support image generation"
        }

    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResponse:
        """Generate video using Doubao"""
        try:
            # Prepare request payload for Doubao
            payload = {
                "req_key": self.api_key,
                "prompt": request.prompt,
            }

            # Add image reference if provided
            if request.image_url:
                payload["image_url"] = request.image_url

            if request.first_frame_url and request.last_frame_url:
                payload["img_urls"] = [request.first_frame_url, request.last_frame_url]
                payload["ref_mode"] = "first_last"

            if request.duration:
                payload["video_duration"] = request.duration

            if request.camera_motion:
                payload["camera_motion"] = request.camera_motion

            # Call Doubao API
            url = self.endpoint or "/api/v1/video/generations"

            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            # Doubao returns a task ID for async processing
            task_id = data.get("data", {}).get("task_id")

            if not task_id:
                raise Exception("No task ID returned from Doubao API")

            return VideoGenerationResponse(
                video_url="",
                task_id=task_id,
                status="processing"
            )

        except httpx.HTTPStatusError as e:
            error_msg = f"Doubao API error: {e.response.status_code} - {e.response.text}"
            try:
                error_data = e.response.json()
                error_msg = f"Doubao API error: {error_data.get('message', error_msg)}"
            except:
                pass

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
                # Default query endpoint for Doubao
                url = f"/api/v1/video/task/{task_id}"
            else:
                url = self.query_endpoint.format(taskId=task_id)

            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()

            status_code = data.get("code", 0)
            status_data = data.get("data", {})

            # Map Doubao status to our status
            if status_code == 0 and status_data.get("status") == "success":
                return {
                    "status": "completed",
                    "result": {
                        "video_url": status_data.get("video_url"),
                        "cover_url": status_data.get("cover_url"),
                        "duration": status_data.get("duration")
                    }
                }
            elif status_data.get("status") == "processing":
                return {
                    "status": "processing",
                    "progress": status_data.get("progress", 0)
                }
            elif status_data.get("status") == "failed":
                return {
                    "status": "failed",
                    "error": status_data.get("error_msg", "Generation failed")
                }
            else:
                return {
                    "status": "pending"
                }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
