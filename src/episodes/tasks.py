"""
Episodes 模块后台任务

处理集数完成后的视频合成等后台任务
"""
import logging
from typing import Any

from sqlalchemy import select

from app.models.drama import Episode, Storyboard, VideoGeneration
from src.core.config import settings

logger = logging.getLogger(__name__)


async def process_episode_finalization(
    episode_id: int,
    timeline_data: dict[str, Any] | None,
    task_id: str
):
    """
    处理集数完成的后台任务

    获取集数的所有分镜和视频，合并成最终视频

    Args:
        episode_id: 集数ID
        timeline_data: 时间线数据（可选）
        task_id: 任务ID
    """
    from app.services.ffmpeg_service import FFmpegService
    from app.utils.file import get_file_url
    from src.core.database import async_session_maker

    ffmpeg_service = FFmpegService(output_dir=settings.LOCAL_STORAGE_PATH)

    async with async_session_maker() as db:
        try:
            # 获取集数
            episode_result = await db.execute(
                select(Episode).where(Episode.id == episode_id)
            )
            episode = episode_result.scalar_one_or_none()

            if not episode:
                logger.warning(f"Episode {episode_id} not found for finalization")
                return

            # 获取所有分镜
            storyboard_result = await db.execute(
                select(Storyboard)
                .where(Storyboard.episode_id == episode_id)
                .order_by(Storyboard.storyboard_number)
            )
            storyboards = storyboard_result.scalars().all()

            if not storyboards:
                # 没有分镜，直接标记为完成
                episode.status = "completed"
                await db.commit()
                logger.info(f"Episode {episode_id} finalized (no storyboards)")
                return

            # 收集视频片段
            clips = []

            if timeline_data and "clips" in timeline_data:
                # 使用提供的时间线数据
                for clip_data in timeline_data["clips"]:
                    clips.append({
                        "scene_id": clip_data.get("scene_id"),
                        "video_url": clip_data.get("video_url"),
                        "start_time": clip_data.get("start_time", 0),
                        "end_time": clip_data.get("end_time", 5),
                        "duration": clip_data.get("duration", 5),
                        "order": clip_data.get("order", 0)
                    })
            else:
                # 使用默认分镜顺序
                for idx, storyboard in enumerate(storyboards):
                    # 获取该分镜的视频生成记录
                    video_gen_result = await db.execute(
                        select(VideoGeneration)
                        .where(
                            VideoGeneration.storyboard_id == storyboard.id,
                            VideoGeneration.status == "completed"
                        )
                        .order_by(VideoGeneration.created_at.desc())
                        .limit(1)
                    )
                    video_gen = video_gen_result.scalar_one_or_none()

                    if video_gen and video_gen.video_url:
                        clips.append({
                            "scene_id": storyboard.scene_id if hasattr(storyboard, 'scene_id') else storyboard.id,
                            "video_url": video_gen.video_url,
                            "start_time": 0,
                            "end_time": video_gen.duration or 5,
                            "duration": video_gen.duration or 5,
                            "order": idx
                        })

            if not clips:
                # 没有可用的视频片段
                episode.status = "completed"
                await db.commit()
                logger.info(f"Episode {episode_id} finalized (no video clips)")
                return

            # 使用 FFmpeg 合并视频
            output_filename = f"episode_{episode_id}_finalized.mp4"
            output_path = f"{settings.LOCAL_STORAGE_PATH}/{output_filename}"

            merge_result = await ffmpeg_service.merge_videos(
                video_clips=clips,
                output_path=output_path
            )

            if merge_result.get("success"):
                # 生成视频URL
                video_url = get_file_url(output_filename, settings.BASE_URL)

                # 更新集数信息
                episode.video_url = video_url
                episode.duration = merge_result.get("total_duration", 0)
                episode.status = "completed"
                await db.commit()
                logger.info(f"Episode {episode_id} finalized successfully: {video_url}")
            else:
                # 合并失败
                episode.status = "failed"
                await db.commit()
                logger.error(f"Failed to merge videos for episode {episode_id}")

        except Exception as e:
            logger.error(f"Error processing episode finalization: {str(e)}")
            # 标记为失败
            try:
                episode_result = await db.execute(
                    select(Episode).where(Episode.id == episode_id)
                )
                episode = episode_result.scalar_one_or_none()
                if episode:
                    episode.status = "failed"
                    await db.commit()
            except Exception as commit_error:
                logger.error(f"Failed to update episode status: {str(commit_error)}")
