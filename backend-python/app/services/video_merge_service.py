from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any, Optional
from app.models.video_merge import VideoMerge, VideoMergeStatus
from app.models.drama import Episode, Drama
from app.utils.video import get_video_processor
from app.utils.logger import log
from app.services.task_service import TaskService
from app.core.config import settings
import os
import uuid


class VideoMergeService:
    """Service for merging videos"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.video_processor = get_video_processor()

    async def merge_videos(
        self,
        episode_id: int,
        drama_id: int,
        title: str,
        scenes: List[Dict[str, Any]],
        provider: str = "ffmpeg",
        model: Optional[str] = None
    ) -> VideoMerge:
        """
        Merge video scenes into a single video

        Args:
            episode_id: Episode ID
            drama_id: Drama ID
            title: Merge title
            scenes: List of scene clips with video URLs and timing
            provider: Merge provider (ffmpeg, etc.)
            model: Optional model name

        Returns:
            VideoMerge record
        """
        try:
            # Verify episode and drama exist
            result = await self.db.execute(
                select(Episode).where(Episode.id == episode_id)
            )
            episode = result.scalar_one_or_none()

            if not episode:
                raise ValueError(f"Episode {episode_id} not found")

            if episode.drama_id != drama_id:
                raise ValueError(f"Episode {episode_id} does not belong to drama {drama_id}")

            # Extract video URLs from scenes
            video_paths = []
            for scene in scenes:
                video_url = scene.get("video_url", "")
                if video_url and not video_url.startswith("http"):
                    # Local file path
                    if os.path.exists(video_url):
                        video_paths.append(video_url)
                    else:
                        log.warning(f"Video file not found: {video_url}")
                elif video_url.startswith("http"):
                    # Remote URL - would need to download first
                    log.warning(f"Remote URLs not yet supported: {video_url}")

            if not video_paths:
                raise ValueError("No valid video files found in scenes")

            # Create video merge record
            video_merge = VideoMerge(
                episode_id=episode_id,
                drama_id=drama_id,
                title=title,
                provider=provider,
                model=model,
                scenes=scenes,
                status=VideoMergeStatus.PROCESSING.value
            )

            self.db.add(video_merge)
            await self.db.commit()
            await self.db.refresh(video_merge)

            # Generate output path
            output_filename = f"merge_{episode_id}_{uuid.uuid4()}.mp4"
            output_path = os.path.join(settings.LOCAL_STORAGE_PATH, output_filename)
            output_url = f"{settings.BASE_URL}/{output_filename}"

            # Merge videos asynchronously
            task_id = f"video_merge_{video_merge.id}"
            video_merge.task_id = task_id
            await self.db.commit()

            # Start background merge task
            task_service = TaskService(self.db)

            async def merge_task(task_id: str, update_callback, **kwargs):
                update_callback(10, "Preparing video merge...")

                # Get transition duration from first scene
                transition_duration = 0.5
                transition_type = "fade"
                if scenes and len(scenes) > 0:
                    transition = scenes[0].get("transition", {})
                    transition_duration = transition.get("duration", 0.5)
                    transition_type = transition.get("type", "fade")

                update_callback(30, "Merging videos...")
                success = await self.video_processor.merge_videos(
                    video_paths,
                    output_path,
                    transition_duration=transition_duration / 1000,  # Convert ms to seconds
                    transition_type=transition_type
                )

                if success:
                    update_callback(90, "Finalizing...")

                    # Get video duration
                    info = await self.video_processor.get_video_info(output_path)
                    duration = info.get("duration", 0) if info else 0

                    # Update record
                    video_merge.merged_url = output_url
                    video_merge.duration = int(duration)
                    video_merge.status = VideoMergeStatus.COMPLETED.value

                    await self.db.commit()

                    update_callback(100, "Completed")
                    log.info(f"Video merge completed: {video_merge.id}")

                    return {"merge_id": video_merge.id, "output_path": output_path}
                else:
                    video_merge.status = VideoMergeStatus.FAILED.value
                    video_merge.error_msg = "Failed to merge videos"
                    await self.db.commit()

                    raise Exception("Video merge failed")

            await task_service.create_task(
                task_type="video_merge",
                resource_id=str(video_merge.id),
                background_func=merge_task
            )

            log.info(f"Started video merge {video_merge.id}")
            return video_merge

        except Exception as e:
            log.error(f"Error creating video merge: {str(e)}")
            raise

    async def get_merge_status(self, merge_id: int) -> Dict[str, Any]:
        """
        Get status of video merge

        Args:
            merge_id: Video merge ID

        Returns:
            Status dict
        """
        result = await self.db.execute(
            select(VideoMerge).where(VideoMerge.id == merge_id)
        )
        video_merge = result.scalar_one_or_none()

        if not video_merge:
            raise ValueError(f"Video merge {merge_id} not found")

        return {
            "status": video_merge.status,
            "merged_url": video_merge.merged_url,
            "duration": video_merge.duration,
            "error": video_merge.error_msg,
            "task_id": video_merge.task_id
        }
