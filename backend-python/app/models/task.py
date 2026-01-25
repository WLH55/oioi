from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from app.core.database import Base


class AsyncTask(Base):
    __tablename__ = "async_tasks"

    id = Column(String(36), primary_key=True)
    type = Column(String(50), nullable=False, index=True)  # storyboard_generation, etc.
    status = Column(String(20), nullable=False, index=True)  # pending, processing, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    message = Column(String(500), nullable=True)
    error = Column(String, nullable=True)
    result = Column(String, nullable=True)  # JSON string
    resource_id = Column(String(36), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
