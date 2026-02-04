"""
资源数据库模型

定义资源相关的数据库表结构。
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base
import enum


class AssetType(str, enum.Enum):
    """资源类型枚举"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class Asset(Base):
    """
    资源模型

    用于管理项目中生成的各种媒体资源（图片、视频、音频）。
    """
    __tablename__ = "assets"

    # 主键和时间戳
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # 关联 ID
    drama_id = Column(Integer, ForeignKey("dramas.id"), nullable=True, index=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=True, index=True)
    storyboard_id = Column(Integer, ForeignKey("storyboards.id"), nullable=True, index=True)
    storyboard_num = Column(Integer, nullable=True)

    # 基本信息
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(20), nullable=False, index=True)
    category = Column(String(50), nullable=True, index=True)

    # URL 信息
    url = Column(String(1000), nullable=False)
    thumbnail_url = Column(String(1000), nullable=True)
    local_path = Column(String(500), nullable=True)

    # 文件属性
    file_size = Column(Float, nullable=True)
    mime_type = Column(String(100), nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    duration = Column(Integer, nullable=True)
    format = Column(String(50), nullable=True)

    # 生成记录关联
    image_gen_id = Column(Integer, ForeignKey("image_generations.id"), nullable=True, index=True)
    video_gen_id = Column(Integer, ForeignKey("video_generations.id"), nullable=True, index=True)

    # 用户交互
    is_favorite = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)

    # 关系
    drama = relationship("Drama")
    image_gen = relationship("ImageGeneration", back_populates="assets")
    video_gen = relationship("VideoGeneration")
