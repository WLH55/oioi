"""
Tasks 模块的 Pydantic 模型
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    """任务基础模型"""
    type: str = Field(..., description="任务类型", max_length=50)
    status: str = Field(..., description="任务状态", max_length=20)
    progress: int = Field(0, description="进度 0-100", ge=0, le=100)


class TaskCreate(BaseModel):
    """创建任务请求模型（内部使用）"""
    type: str = Field(..., description="任务类型")
    resource_id: str = Field(..., description="关联资源ID")


class TaskUpdate(BaseModel):
    """更新任务请求模型"""
    status: str | None = Field(None, description="任务状态")
    progress: int | None = Field(None, description="进度", ge=0, le=100)
    message: str | None = Field(None, description="进度消息")
    error: str | None = Field(None, description="错误信息")
    result: str | None = Field(None, description="结果")


class TaskResponse(TaskBase):
    """任务响应模型"""
    id: str
    message: str | None = None
    error: str | None = None
    result: dict[str, Any] | None = None
    resource_id: str
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """任务列表响应模型"""
    total: int
    items: list[TaskResponse]


class TaskStatusResponse(BaseModel):
    """任务状态响应模型"""
    task_id: str
    status: str
    progress: int
    message: str | None = None


class TaskCancelResponse(BaseModel):
    """任务取消响应模型"""
    message: str
    task_id: str
    canceled: bool
