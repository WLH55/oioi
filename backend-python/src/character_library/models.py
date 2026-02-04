"""
角色库数据库模型

定义角色库相关的数据库表结构。
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from src.database import Base


class CharacterLibrary(Base):
    """角色库模型"""
    __tablename__ = "character_libraries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=True)
    image_url = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)
    source_type = Column(String(20), default="generated")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
