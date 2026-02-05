"""
Tasks 模块依赖注入

提供 FastAPI 依赖注入函数
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import AsyncTask
from src.database import get_db

from .exceptions import TaskNotFound
from .service import TaskService


async def get_task_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    """
    获取 TaskService 实例

    Args:
        db: 数据库会话

    Returns:
        TaskService 实例
    """
    return TaskService(db)


async def valid_task_id(
    task_id: str,
    service: TaskService = Depends(get_task_service)
) -> AsyncTask:
    """
    验证任务ID是否有效

    Args:
        task_id: 任务ID
        service: TaskService 实例

    Returns:
        AsyncTask 对象

    Raises:
        TaskNotFound: 任务不存在
    """
    try:
        return await service.get_by_id(task_id)
    except TaskNotFound:
        raise


# 类型别名，方便在其他模块中使用
ServiceDep = Annotated[TaskService, Depends(get_task_service)]
TaskDep = Annotated[AsyncTask, Depends(valid_task_id)]
