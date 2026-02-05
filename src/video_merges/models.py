"""
视频合成模块数据库模型

定义视频合成记录相关的 SQLAlchemy 模型。
"""
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class VideoMerge(Base):
    """视频合成记录"""
    __tablename__ = "video_merges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    episode_id: Mapped[int] = mapped_column(Integer, nullable=False)
    drama_id: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=True)
    provider: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending")  # pending, processing, completed, failed
    scenes: Mapped[str] = mapped_column(Text, nullable=False)  # JSON - 场景片段列表
    merged_url: Mapped[str] = mapped_column(String, nullable=True)
    duration: Mapped[int] = mapped_column(Integer, nullable=True)  # 总时长(秒)
    task_id: Mapped[str] = mapped_column(String, nullable=True)
    error_msg: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
