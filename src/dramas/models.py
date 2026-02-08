"""
剧本模块数据库模型

定义剧本相关的 SQLAlchemy 模型。
"""
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Drama(Base):
    """剧本"""
    __tablename__ = "dramas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    genre: Mapped[str] = mapped_column(String, nullable=True)
    style: Mapped[str] = mapped_column(String, default="realistic")  # 风格
    total_episodes: Mapped[int] = mapped_column(Integer, default=1)  # 总集数
    total_duration: Mapped[int] = mapped_column(Integer, default=0)  # 总时长(秒)
    status: Mapped[str] = mapped_column(String, default="draft")  # draft, in_progress, completed
    thumbnail: Mapped[str] = mapped_column(String, nullable=True)
    tags: Mapped[str] = mapped_column(Text, nullable=True)  # JSON 存储
    meta_data: Mapped[str] = mapped_column(Text, nullable=True)  # JSON 存储
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
