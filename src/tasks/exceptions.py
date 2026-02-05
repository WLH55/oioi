"""
Tasks 模块异常类
"""
from src.exceptions import BusinessValidationException


class TaskNotFound(BusinessValidationException):
    """任务不存在异常"""

    def __init__(self, task_id: str = None):
        message = "任务不存在" + (f" (ID: {task_id})" if task_id else "")
        super().__init__(message)


class TaskCannotBeCanceled(BusinessValidationException):
    """任务无法取消异常"""

    def __init__(self, reason: str = "任务无法取消"):
        super().__init__(f"任务取消失败: {reason}")


class InvalidTaskStatus(BusinessValidationException):
    """无效的任务状态异常"""

    def __init__(self, status: str):
        super().__init__(f"无效的任务状态: {status}")
