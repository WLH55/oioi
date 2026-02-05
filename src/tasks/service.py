"""
Tasks 模块服务层

提供异步任务管理相关的业务逻辑处理
"""
import asyncio
import logging
import uuid
from collections.abc import Callable
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.tasks.models import Task

from .exceptions import TaskNotFound

logger = logging.getLogger(__name__)


class TaskService:
    """任务服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.running_tasks: dict[str, asyncio.Task] = {}

    async def get_by_id(self, task_id: str) -> AsyncTask:
        """
        根据ID获取任务

        Args:
            task_id: 任务ID

        Returns:
            AsyncTask 对象

        Raises:
            TaskNotFound: 任务不存在
        """
        result = await self.db.execute(
            select(AsyncTask).where(AsyncTask.id == task_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            raise TaskNotFound(task_id)

        return task

    async def get_list(
        self,
        resource_id: str | None = None,
        task_type: str | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[AsyncTask], int]:
        """
        获取任务列表

        Args:
            resource_id: 资源ID，可选
            task_type: 任务类型，可选
            skip: 跳过数量
            limit: 限制数量

        Returns:
            (任务列表, 总数)
        """
        query = select(AsyncTask)

        if resource_id:
            query = query.where(AsyncTask.resource_id == resource_id)
        if task_type:
            query = query.where(AsyncTask.type == task_type)

        # 获取总数
        from sqlalchemy import func
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # 获取分页数据
        query = query.offset(skip).limit(limit)
        query = query.order_by(AsyncTask.created_at.desc())

        result = await self.db.execute(query)
        tasks = result.scalars().all()

        return list(tasks), total

    async def create(
        self,
        task_type: str,
        resource_id: str,
        background_func: Callable,
        **kwargs
    ) -> AsyncTask:
        """
        创建新任务

        Args:
            task_type: 任务类型
            resource_id: 关联资源ID
            background_func: 后台执行函数
            **kwargs: 传递给后台函数的额外参数

        Returns:
            创建的 AsyncTask 对象
        """
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

        # 启动后台任务
        async_task = asyncio.create_task(
            self._run_background_task(task_id, background_func, **kwargs)
        )
        self.running_tasks[task_id] = async_task

        logger.info(f"Created task {task_id} of type {task_type}")
        return task

    async def _run_background_task(
        self,
        task_id: str,
        background_func: Callable,
        **kwargs
    ):
        """
        运行后台任务并更新状态

        Args:
            task_id: 任务ID
            background_func: 后台函数
            **kwargs: 传递给后台函数的参数
        """
        try:
            # 更新状态为处理中
            await self.update_status(task_id, status="processing", progress=0)

            # 执行后台函数
            result = await background_func(
                task_id=task_id,
                update_callback=lambda progress, message: self._update_progress(
                    task_id, progress, message
                ),
                **kwargs
            )

            # 更新为完成状态
            await self.update_status(
                task_id,
                status="completed",
                progress=100,
                result=str(result) if result else None
            )

            logger.info(f"Task {task_id} completed successfully")

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Task {task_id} failed: {error_msg}")

            # 更新为失败状态
            await self.update_status(
                task_id,
                status="failed",
                error=error_msg
            )

        finally:
            # 从运行任务中移除
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]

    async def _update_progress(self, task_id: str, progress: int, message: str):
        """
        更新任务进度

        Args:
            task_id: 任务ID
            progress: 进度
            message: 消息
        """
        await self.update_status(task_id, progress=progress, message=message)

    async def update_status(
        self,
        task_id: str,
        status: str | None = None,
        progress: int | None = None,
        message: str | None = None,
        error: str | None = None,
        result: str | None = None
    ):
        """
        更新任务状态

        Args:
            task_id: 任务ID
            status: 状态
            progress: 进度
            message: 消息
            error: 错误
            result: 结果
        """
        try:
            task = await self.get_by_id(task_id)

            if status is not None:
                task.status = status
                if status == "completed":
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
            logger.error(f"Error updating task status: {str(e)}")

    async def cancel(self, task_id: str) -> bool:
        """
        取消运行中的任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功取消
        """
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.cancel()

            await self.update_status(
                task_id,
                status="failed",
                error="任务已取消"
            )

            return True

        return False

    async def get_resource_tasks(
        self,
        resource_id: str,
        task_type: str | None = None
    ) -> list[AsyncTask]:
        """
        获取资源的所有任务

        Args:
            resource_id: 资源ID
            task_type: 任务类型，可选

        Returns:
            AsyncTask 列表
        """
        query = select(AsyncTask).where(AsyncTask.resource_id == resource_id)

        if task_type:
            query = query.where(AsyncTask.type == task_type)

        query = query.order_by(AsyncTask.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())


# ============================================================================
# 辅助函数 - 创建常见任务
# ============================================================================

async def create_image_generation_task(
    task_service: TaskService,
    image_gen_id: int,
    drama_id: int
) -> AsyncTask:
    """
    创建图片生成任务

    Args:
        task_service: TaskService 实例
        image_gen_id: 图片生成ID
        drama_id: 剧目ID

    Returns:
        AsyncTask 对象
    """

    async def generate_image(
        task_id: str,
        update_callback: Callable,
        image_gen_id: int,
        drama_id: int
    ):
        # TODO: 实际实现应调用图片生成服务
        update_callback(10, "初始化 AI 提供商...")
        await asyncio.sleep(1)
        update_callback(50, "生成图片中...")
        await asyncio.sleep(1)
        update_callback(90, "处理结果...")
        await asyncio.sleep(0.5)
        update_callback(100, "完成")
        return {"image_gen_id": image_gen_id}

    return await task_service.create(
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
    """
    创建视频生成任务

    Args:
        task_service: TaskService 实例
        video_gen_id: 视频生成ID
        drama_id: 剧目ID

    Returns:
        AsyncTask 对象
    """

    async def generate_video(
        task_id: str,
        update_callback: Callable,
        video_gen_id: int,
        drama_id: int
    ):
        # TODO: 实际实现应调用视频生成服务
        update_callback(10, "初始化 AI 提供商...")
        await asyncio.sleep(2)
        update_callback(30, "生成视频中...")
        await asyncio.sleep(3)
        update_callback(70, "处理视频...")
        await asyncio.sleep(2)
        update_callback(90, "完成处理...")
        await asyncio.sleep(1)
        update_callback(100, "完成")
        return {"video_gen_id": video_gen_id}

    return await task_service.create(
        task_type="video_generation",
        resource_id=str(video_gen_id),
        background_func=generate_video,
        video_gen_id=video_gen_id,
        drama_id=drama_id
    )
