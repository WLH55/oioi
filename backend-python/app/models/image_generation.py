from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ImageGenerationStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ImageType(str, enum.Enum):
    CHARACTER = "character"
    SCENE = "scene"
    STORYBOARD = "storyboard"


class ImageGeneration(Base):
    __tablename__ = "image_generations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    storyboard_id = Column(Integer, ForeignKey("storyboards.id"), nullable=True, index=True)
    drama_id = Column(Integer, ForeignKey("dramas.id"), nullable=False, index=True)
    scene_id = Column(Integer, ForeignKey("scenes.id"), nullable=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=True, index=True)
    image_type = Column(String(20), default=ImageType.STORYBOARD.value, nullable=False, index=True)
    frame_type = Column(String(20), nullable=True)  # first, key, last, panel, action
    provider = Column(String(50), nullable=False)
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    model = Column(String(100), nullable=True)
    size = Column(String(20), nullable=True)
    quality = Column(String(20), nullable=True)
    style = Column(String(50), nullable=True)
    steps = Column(Integer, nullable=True)
    cfg_scale = Column(Float, nullable=True)
    seed = Column(Float, nullable=True)
    image_url = Column(Text, nullable=True)
    minio_url = Column(Text, nullable=True)
    local_path = Column(Text, nullable=True)
    status = Column(String(20), default=ImageGenerationStatus.PENDING.value, nullable=False)
    task_id = Column(String(200), nullable=True)
    error_msg = Column(Text, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    reference_images = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    storyboard = relationship("Storyboard")
    drama = relationship("Drama")
    scene = relationship("Scene")
    character = relationship("Character")
    assets = relationship("Asset", back_populates="image_gen")
