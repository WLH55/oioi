from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from app.core.database import Base


class CharacterLibrary(Base):
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
