"""
AI 配置模块数据库模型

定义 AI 服务配置相关的 SQLAlchemy 模型。
"""
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Text, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class AIServiceConfig(Base):
    """AI 服务配置"""
    __tablename__ = "ai_service_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    service_type: Mapped[str] = mapped_column(String, nullable=False)  # text, image, video
    provider: Mapped[str] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    base_url: Mapped[str] = mapped_column(String, nullable=False)
    api_key: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=True)
    endpoint: Mapped[str] = mapped_column(String, nullable=True)
    query_endpoint: Mapped[str] = mapped_column(String, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    is_default: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[int] = mapped_column(Integer, default=1)
    settings: Mapped[str] = mapped_column(Text, nullable=True)  # JSON
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class AIServiceProvider(Base):
    """AI 服务提供商"""
    __tablename__ = "ai_service_providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    service_type: Mapped[str] = mapped_column(String, nullable=False)  # text, image, video
    default_url: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
