from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class AssetType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    drama_id = Column(Integer, ForeignKey("dramas.id"), nullable=True, index=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=True, index=True)
    storyboard_id = Column(Integer, ForeignKey("storyboards.id"), nullable=True, index=True)
    storyboard_num = Column(Integer, nullable=True)

    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(20), nullable=False, index=True)
    category = Column(String(50), nullable=True, index=True)
    url = Column(String(1000), nullable=False)
    thumbnail_url = Column(String(1000), nullable=True)
    local_path = Column(String(500), nullable=True)

    file_size = Column(Float, nullable=True)
    mime_type = Column(String(100), nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    duration = Column(Integer, nullable=True)
    format = Column(String(50), nullable=True)

    image_gen_id = Column(Integer, ForeignKey("image_generations.id"), nullable=True, index=True)
    video_gen_id = Column(Integer, ForeignKey("video_generations.id"), nullable=True, index=True)

    is_favorite = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)

    # Relationships
    drama = relationship("Drama")
    image_gen = relationship("ImageGeneration", back_populates="assets")
    video_gen = relationship("VideoGeneration")
