from sqlalchemy import Column, Integer, String, Text, Enum as SQLEnum, DateTime, ForeignKey, JSON, Float, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class DramaStatus(str, enum.Enum):
    DRAFT = "draft"
    PRODUCING = "producing"
    COMPLETED = "completed"


# Many-to-many relationship table for Character-Episode
episode_characters = Table(
    'episode_characters',
    Base.metadata,
    Column('episode_id', Integer, ForeignKey('episodes.id', ondelete='CASCADE'), primary_key=True),
    Column('character_id', Integer, ForeignKey('characters.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False)
)


class Drama(Base):
    __tablename__ = "dramas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    genre = Column(String(50), nullable=True)
    style = Column(String(50), default="realistic", nullable=False)
    total_episodes = Column(Integer, default=1)
    total_duration = Column(Integer, default=0)
    status = Column(String(20), default=DramaStatus.DRAFT.value, nullable=False)
    thumbnail = Column(String(500), nullable=True)
    tags = Column(JSON, nullable=True)
    meta_data = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Relationships
    episodes = relationship("Episode", back_populates="drama", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="drama", cascade="all, delete-orphan")
    scenes = relationship("Scene", back_populates="drama", cascade="all, delete-orphan")


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    drama_id = Column(Integer, ForeignKey("dramas.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    appearance = Column(Text, nullable=True)
    personality = Column(Text, nullable=True)
    voice_style = Column(String(200), nullable=True)
    image_url = Column(String(500), nullable=True)
    reference_images = Column(JSON, nullable=True)
    seed_value = Column(String(100), nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Relationships
    drama = relationship("Drama", back_populates="characters")
    episodes = relationship("Episode", secondary=episode_characters, back_populates="characters")


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    drama_id = Column(Integer, ForeignKey("dramas.id"), nullable=False, index=True)
    episode_number = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    script_content = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    duration = Column(Integer, default=0)  # Total duration in seconds
    status = Column(String(20), default=DramaStatus.DRAFT.value)
    video_url = Column(String(500), nullable=True)
    thumbnail = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Relationships
    drama = relationship("Drama", back_populates="episodes")
    characters = relationship("Character", secondary=episode_characters, back_populates="episodes")
    storyboards = relationship("Storyboard", back_populates="episode", cascade="all, delete-orphan")
    scenes = relationship("Scene", back_populates="episode", cascade="all, delete-orphan")


class Scene(Base):
    __tablename__ = "scenes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    drama_id = Column(Integer, ForeignKey("dramas.id"), nullable=False, index=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=True, index=True)
    location = Column(String(200), nullable=False)
    time = Column(String(100), nullable=False)
    prompt = Column(Text, nullable=False)
    storyboard_count = Column(Integer, default=1)
    image_url = Column(String(500), nullable=True)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Relationships
    drama = relationship("Drama", back_populates="scenes")
    episode = relationship("Episode", back_populates="scenes")


class Storyboard(Base):
    __tablename__ = "storyboards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    drama_id = Column(Integer, ForeignKey("dramas.id"), nullable=False, index=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=False, index=True)
    scene_id = Column(Integer, ForeignKey("scenes.id"), nullable=True, index=True)
    storyboard_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    time = Column(String(255), nullable=True)
    shot_type = Column(String(100), nullable=True)
    angle = Column(String(100), nullable=True)
    movement = Column(String(100), nullable=True)
    action = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    atmosphere = Column(Text, nullable=True)
    image_prompt = Column(Text, nullable=True)
    video_prompt = Column(Text, nullable=True)
    bgm_prompt = Column(Text, nullable=True)
    sound_effect = Column(String(255), nullable=True)
    dialogue = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    duration = Column(Integer, default=5)
    composed_image = Column(Text, nullable=True)
    video_url = Column(Text, nullable=True)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Relationships
    drama = relationship("Drama")
    episode = relationship("Episode", back_populates="storyboards")
    scene = relationship("Scene")
