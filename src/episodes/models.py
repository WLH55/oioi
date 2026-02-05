"""
分集模块数据库模型

定义剧本分集相关的 SQLAlchemy 模型。
"""
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Episode(Base):
    """剧本分集"""
    __tablename__ = "episodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    drama_id: Mapped[int] = mapped_column(Integer, nullable=False)
    episode_number: Mapped[int] = mapped_column(Integer, nullable=False)  # 集数序号
    title: Mapped[str] = mapped_column(String, nullable=False)
    script_content: Mapped[str] = mapped_column(Text, nullable=True)  # 剧本内容
    description: Mapped[str] = mapped_column(Text, nullable=True)
    duration: Mapped[int] = mapped_column(Integer, default=0)  # 时长(秒)
    status: Mapped[str] = mapped_column(String, default="draft")
    video_url: Mapped[str] = mapped_column(String, nullable=True)
    thumbnail: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
