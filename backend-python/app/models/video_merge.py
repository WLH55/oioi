from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class VideoMergeStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoMerge(Base):
    __tablename__ = "video_merges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=False, index=True)
    drama_id = Column(Integer, ForeignKey("dramas.id"), nullable=False, index=True)
    title = Column(String(200), nullable=True)
    provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=True)
    status = Column(String(20), default=VideoMergeStatus.PENDING.value, nullable=False)
    scenes = Column(JSON, nullable=False)  # JSON array of scene clips
    merged_url = Column(String(500), nullable=True)
    duration = Column(Integer, nullable=True)
    task_id = Column(String(100), nullable=True)
    error_msg = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    episode = relationship("Episode")
    drama = relationship("Drama")
