"""
AI 配置数据库模型

定义 AI 服务配置相关的数据库表结构。
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

from src.database import Base


class AIServiceConfig(Base):
    """AI 服务配置模型"""
    __tablename__ = "ai_service_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_type = Column(String(50), nullable=False)  # text, image, video
    provider = Column(String(50), nullable=False)  # openai, gemini, volcengine, etc.
    name = Column(String(100), nullable=False)
    base_url = Column(String(255), nullable=False)
    api_key = Column(String(255), nullable=False)
    model = Column(Text, nullable=False)  # JSON string of model array
    endpoint = Column(String(255), nullable=True)
    query_endpoint = Column(String(255), nullable=True)
    priority = Column(Integer, default=0)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    settings = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
