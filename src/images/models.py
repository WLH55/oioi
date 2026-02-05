"""
图片生成模块数据库模型

定义图片生成记录相关的 SQLAlchemy 模型。
"""
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Text, Float
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class ImageGeneration(Base):
    """图片生成记录"""
    __tablename__ = "image_generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    storyboard_id: Mapped[int] = mapped_column(Integer, nullable=True)
    drama_id: Mapped[int] = mapped_column(Integer, nullable=False)
    provider: Mapped[str] = mapped_column(String, nullable=False)  # openai, midjourney, stable_diffusion
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    negative_prompt: Mapped[str] = mapped_column(Text, nullable=True)
    model: Mapped[str] = mapped_column(String, nullable=True)
    size: Mapped[str] = mapped_column(String, nullable=True)  # 如 1024x1024
    quality: Mapped[str] = mapped_column(String, nullable=True)
    style: Mapped[str] = mapped_column(String, nullable=True)
    steps: Mapped[int] = mapped_column(Integer, nullable=True)
    cfg_scale: Mapped[float] = mapped_column(Float, nullable=True)
    seed: Mapped[int] = mapped_column(Integer, nullable=True)
    image_url: Mapped[str] = mapped_column(String, nullable=True)
    minio_url: Mapped[str] = mapped_column(String, nullable=True)
    local_path: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending")  # pending, processing, completed, failed
    task_id: Mapped[str] = mapped_column(String, nullable=True)
    error_msg: Mapped[str] = mapped_column(Text, nullable=True)
    width: Mapped[int] = mapped_column(Integer, nullable=True)
    height: Mapped[int] = mapped_column(Integer, nullable=True)
    reference_images: Mapped[str] = mapped_column(Text, nullable=True)  # JSON
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
