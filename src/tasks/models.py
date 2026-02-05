"""
任务模块数据库模型

定义任务相关的 SQLAlchemy 模型。
"""
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Task(Base):
    """任务"""
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_type: Mapped[str] = mapped_column(String, nullable=False)  # image, video, audio, merge
    provider: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending")  # pending, processing, completed, failed
    input_data: Mapped[str] = mapped_column(Text, nullable=True)  # JSON
    result_data: Mapped[str] = mapped_column(Text, nullable=True)  # JSON
    progress: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
