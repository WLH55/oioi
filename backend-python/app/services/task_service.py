from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any, Callable
from app.models.task import AsyncTask
from app.utils.logger import log
import asyncio
import uuid


class TaskService:
    """Service for managing async tasks"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.running_tasks: Dict[str, asyncio.Task] = {}

    async def create_task(
        self,
        task_type: str,
        resource_id: str,
        background_func: Callable,
        **kwargs
    ) -> AsyncTask:
        """
        Create a new async task

        Args:
            task_type: Type of task (e.g., 'storyboard_generation', 'image_generation')
            resource_id: Associated resource ID
            background_func: Async function to execute
            **kwargs: Additional arguments to pass to background_func

        Returns:
            Created AsyncTask
        """
        try:
            # Create task record
            task_id = str(uuid.uuid4())
            task = AsyncTask(
                id=task_id,
                type=task_type,
                status="pending",
                progress=0,
                resource_id=resource_id
            )

            self.db.add(task)
            await self.db.commit()
            await self.db.refresh(task)

            # Start background task
            async_task = asyncio.create_task(
                self._run_background_task(task_id, background_func, **kwargs)
            )
            self.running_tasks[task_id] = async_task

            log.info(f"Created task {task_id} of type {task_type}")
            return task

        except Exception as e:
            log.error(f"Error creating task: {str(e)}")
            raise

    async def _run_background_task(
        self,
        task_id: str,
        background_func: Callable,
        **kwargs
    ):
        """Run background task and update status"""
        try:
            # Update status to processing
            await self.update_task_status(task_id, status="processing", progress=0)

            # Execute background function
            result = await background_func(
                task_id=task_id,
                update_callback=lambda progress, message: self._update_task_progress(
                    task_id, progress, message
                ),
                **kwargs
            )

            # Update to completed
            await self.update_task_status(
                task_id,
                status="completed",
                progress=100,
                result=str(result) if result else None
            )

            log.info(f"Task {task_id} completed successfully")

        except Exception as e:
            error_msg = str(e)
            log.error(f"Task {task_id} failed: {error_msg}")

            # Update to failed
            await self.update_task_status(
                task_id,
                status="failed",
                error=error_msg
            )

        finally:
            # Remove from running tasks
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]

    async def _update_task_progress(self, task_id: str, progress: int, message: str):
        """Update task progress"""
        await self.update_task_status(task_id, progress=progress, message=message)

    async def update_task_status(
        self,
        task_id: str,
        status: Optional[str] = None,
        progress: Optional[int] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
        result: Optional[str] = None
    ):
        """Update task status"""
        try:
            db_task = await self.db.execute(
                select(AsyncTask).where(AsyncTask.id == task_id)
            )
            task = db_task.scalar_one_or_none()

            if not task:
                log.warning(f"Task {task_id} not found for status update")
                return

            if status is not None:
                task.status = status
                if status == "completed":
                    from datetime import datetime
                    task.completed_at = datetime.utcnow()

            if progress is not None:
                task.progress = max(0, min(100, progress))

            if message is not None:
                task.message = message

            if error is not None:
                task.error = error

            if result is not None:
                task.result = result

            await self.db.commit()

        except Exception as e:
            log.error(f"Error updating task status: {str(e)}")

    async def get_task(self, task_id: str) -> Optional[AsyncTask]:
        """Get task by ID"""
        result = await self.db.execute(
            select(AsyncTask).where(AsyncTask.id == task_id)
        )
        return result.scalar_one_or_none()

    async def get_resource_tasks(
        self,
        resource_id: str,
        task_type: Optional[str] = None
    ) -> list[AsyncTask]:
        """Get all tasks for a resource"""
        query = select(AsyncTask).where(AsyncTask.resource_id == resource_id)

        if task_type:
            query = query.where(AsyncTask.type == task_type)

        query = query.order_by(AsyncTask.created_at.desc())

        result = await self.db.execute(query)
        return result.scalars().all()

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.cancel()

            await self.update_task_status(
                task_id,
                status="failed",
                error="Task cancelled by user"
            )

            return True

        return False


# Helper functions for creating common tasks
async def create_image_generation_task(
    task_service: TaskService,
    image_gen_id: int,
    drama_id: int
) -> AsyncTask:
    """Create an image generation task"""

    async def generate_image(
        task_id: str,
        update_callback: Callable,
        image_gen_id: int,
        drama_id: int
    ):
        # This would call the image generation service
        # For now, it's a placeholder
        update_callback(10, "Initializing AI provider...")

        # Simulate processing
        await asyncio.sleep(1)
        update_callback(50, "Generating image...")

        await asyncio.sleep(1)
        update_callback(90, "Processing results...")

        await asyncio.sleep(0.5)
        update_callback(100, "Completed")

        return {"image_gen_id": image_gen_id}

    return await task_service.create_task(
        task_type="image_generation",
        resource_id=str(image_gen_id),
        background_func=generate_image,
        image_gen_id=image_gen_id,
        drama_id=drama_id
    )


async def create_video_generation_task(
    task_service: TaskService,
    video_gen_id: int,
    drama_id: int
) -> AsyncTask:
    """Create a video generation task"""

    async def generate_video(
        task_id: str,
        update_callback: Callable,
        video_gen_id: int,
        drama_id: int
    ):
        update_callback(10, "Initializing AI provider...")

        # Simulate processing (video takes longer)
        await asyncio.sleep(2)
        update_callback(30, "Generating video...")

        await asyncio.sleep(3)
        update_callback(70, "Processing video...")

        await asyncio.sleep(2)
        update_callback(90, "Finalizing...")

        await asyncio.sleep(1)
        update_callback(100, "Completed")

        return {"video_gen_id": video_gen_id}

    return await task_service.create_task(
        task_type="video_generation",
        resource_id=str(video_gen_id),
        background_func=generate_video,
        video_gen_id=video_gen_id,
        drama_id=drama_id
    )
