from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from app.core.database import Base


class AIServiceConfig(Base):
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


class AIServiceProvider(Base):
    __tablename__ = "ai_service_providers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(100), nullable=False)
    service_type = Column(String(50), nullable=False)
    default_url = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
