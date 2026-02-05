"""
Tasks 模块路由

提供异步任务管理相关的 API 端点
"""

from fastapi import APIRouter, Depends, Query

from src.core.schemas import ApiResponse, ListResponse

from .dependencies import get_task_service
from .schemas import (
    TaskCancelResponse,
    TaskResponse,
)
from .service import TaskService

router = APIRouter()


# ============================================================================
# 任务管理端点
# ============================================================================

@router.get(
    "/list",
    summary="获取任务列表",
    description="获取任务列表，支持按资源和类型筛选，支持分页",
    response_model=ApiResponse[ListResponse[TaskResponse]]
)
async def list_tasks(
    resource_id: str | None = Query(None, description="关联资源ID"),
    task_type: str | None = Query(None, description="任务类型"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    service: TaskService = Depends(get_task_service)
) -> ApiResponse[ListResponse[TaskResponse]]:
    """
    获取任务列表

    - **resource_id**: 可选，筛选指定资源的任务
    - **task_type**: 可选，筛选指定类型的任务
    - **page**: 页码，从1开始
    - **page_size**: 每页数量，最大100
    """
    skip = (page - 1) * page_size
    tasks, total = await service.get_list(
        resource_id=resource_id,
        task_type=task_type,
        skip=skip,
        limit=page_size
    )

    items = [
        TaskResponse.model_validate(task) for task in tasks
    ]

    return ApiResponse.success(data=ListResponse(total=total, items=items))


@router.get(
    "/status",
    summary="获取任务状态",
    description="根据任务ID获取任务状态",
    response_model=ApiResponse[TaskResponse]
)
async def get_task_status(
    task_id: str = Query(..., description="任务ID"),
    service: TaskService = Depends(get_task_service)
) -> ApiResponse[TaskResponse]:
    """
    获取任务状态

    - **task_id**: 任务ID
    """
    task = await service.get_by_id(task_id)
    return ApiResponse.success(data=TaskResponse.model_validate(task))


@router.post(
    "/cancel",
    summary="取消任务",
    description="取消指定的运行中任务",
    response_model=ApiResponse[TaskCancelResponse]
)
async def cancel_task(
    task_id: str = Query(..., description="任务ID"),
    service: TaskService = Depends(get_task_service)
) -> ApiResponse[TaskCancelResponse]:
    """
    取消任务

    - **task_id**: 任务ID

    只能取消状态为 pending 或 processing 的任务
    """
    canceled = await service.cancel(task_id)

    return ApiResponse.success(data=TaskCancelResponse(
        message="任务已取消" if canceled else "任务无法取消或未在运行中",
        task_id=task_id,
        canceled=canceled
    ))


@router.get(
    "/by-resource",
    summary="获取资源的所有任务",
    description="获取指定资源的所有任务",
    response_model=ApiResponse[list[TaskResponse]]
)
async def list_resource_tasks(
    resource_id: str = Query(..., description="资源ID"),
    task_type: str | None = Query(None, description="任务类型，可选"),
    service: TaskService = Depends(get_task_service)
) -> ApiResponse[list[TaskResponse]]:
    """
    获取指定资源的所有任务

    - **resource_id**: 资源ID
    - **task_type**: 可选，筛选特定类型的任务
    """
    tasks = await service.get_resource_tasks(resource_id, task_type)

    items = [
        TaskResponse.model_validate(task) for task in tasks
    ]

    return ApiResponse.success(data=items)
