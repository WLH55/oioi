from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from app.core.database import Base


class FramePrompt(Base):
    __tablename__ = "frame_prompts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    storyboard_id = Column(Integer, nullable=False, index=True)
    frame_type = Column(String(20), nullable=False, index=True)  # first, key, last, panel, action
    prompt = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    layout = Column(String(50), nullable=True)  # Only for panel/action type
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


# Constants
FRAME_TYPE_FIRST = "first"
FRAME_TYPE_KEY = "key"
FRAME_TYPE_LAST = "last"
FRAME_TYPE_PANEL = "panel"
FRAME_TYPE_ACTION = "action"
