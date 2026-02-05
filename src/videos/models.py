"""
视频生成模块数据库模型

定义视频生成记录相关的 SQLAlchemy 模型。
"""
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Text, Float
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class VideoGeneration(Base):
    """视频生成记录"""
    __tablename__ = "video_generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    storyboard_id: Mapped[int] = mapped_column(Integer, nullable=True)
    drama_id: Mapped[int] = mapped_column(Integer, nullable=False)
    provider: Mapped[str] = mapped_column(String, nullable=False)  # runway, pika, doubao, openai
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=True)
    image_gen_id: Mapped[int] = mapped_column(Integer, nullable=True)
    image_url: Mapped[str] = mapped_column(String, nullable=True)
    first_frame_url: Mapped[str] = mapped_column(String, nullable=True)
    duration: Mapped[float] = mapped_column(Float, nullable=True)  # 时长(秒)
    fps: Mapped[int] = mapped_column(Integer, nullable=True)
    resolution: Mapped[str] = mapped_column(String, nullable=True)
    aspect_ratio: Mapped[str] = mapped_column(String, nullable=True)
    style: Mapped[str] = mapped_column(String, nullable=True)
    motion_level: Mapped[int] = mapped_column(Integer, nullable=True)
    camera_motion: Mapped[str] = mapped_column(String, nullable=True)
    seed: Mapped[int] = mapped_column(Integer, nullable=True)
    video_url: Mapped[str] = mapped_column(String, nullable=True)
    minio_url: Mapped[str] = mapped_column(String, nullable=True)
    local_path: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending")  # pending, processing, completed, failed
    task_id: Mapped[str] = mapped_column(String, nullable=True)
    error_msg: Mapped[str] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    width: Mapped[int] = mapped_column(Integer, nullable=True)
    height: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
