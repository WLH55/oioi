from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class VideoStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoGeneration(Base):
    __tablename__ = "video_generations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    storyboard_id = Column(Integer, ForeignKey("storyboards.id"), nullable=True, index=True)
    drama_id = Column(Integer, ForeignKey("dramas.id"), nullable=False, index=True)
    image_gen_id = Column(Integer, ForeignKey("image_generations.id"), nullable=True, index=True)

    provider = Column(String(50), nullable=False)
    prompt = Column(Text, nullable=False)
    model = Column(String(100), nullable=True)

    reference_mode = Column(String(20), nullable=True)  # single, first_last, multiple, none

    image_url = Column(String(1000), nullable=True)
    first_frame_url = Column(String(1000), nullable=True)
    last_frame_url = Column(String(1000), nullable=True)
    reference_image_urls = Column(Text, nullable=True)  # JSON array

    duration = Column(Integer, nullable=True)
    fps = Column(Integer, nullable=True)
    resolution = Column(String(50), nullable=True)
    aspect_ratio = Column(String(20), nullable=True)
    style = Column(String(100), nullable=True)
    motion_level = Column(Integer, nullable=True)
    camera_motion = Column(String(100), nullable=True)
    seed = Column(Float, nullable=True)

    video_url = Column(String(1000), nullable=True)
    minio_url = Column(String(1000), nullable=True)
    local_path = Column(String(500), nullable=True)

    status = Column(String(20), default=VideoStatus.PENDING.value, nullable=False, index=True)
    task_id = Column(String(200), nullable=True, index=True)

    error_msg = Column(Text, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)

    # Relationships
    storyboard = relationship("Storyboard")
    drama = relationship("Drama")
    image_gen = relationship("ImageGeneration")
