from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class TimelineStatus(str, enum.Enum):
    DRAFT = "draft"
    EDITING = "editing"
    COMPLETED = "completed"
    EXPORTING = "exporting"


class Timeline(Base):
    __tablename__ = "timelines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    drama_id = Column(Integer, ForeignKey("dramas.id"), nullable=False, index=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    duration = Column(Integer, default=0)
    fps = Column(Integer, default=30)
    resolution = Column(String(50), nullable=True)
    status = Column(String(20), default=TimelineStatus.DRAFT.value, nullable=False, index=True)

    # Relationships
    drama = relationship("Drama")
    episode = relationship("Episode")
    tracks = relationship("TimelineTrack", back_populates="timeline", cascade="all, delete-orphan")


class TrackType(str, enum.Enum):
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"


class TimelineTrack(Base):
    __tablename__ = "timeline_tracks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    timeline_id = Column(Integer, ForeignKey("timelines.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)
    order = Column(Integer, default=0, nullable=False)
    is_locked = Column(Boolean, default=False)
    is_muted = Column(Boolean, default=False)
    volume = Column(Integer, default=100)

    # Relationships
    timeline = relationship("Timeline", back_populates="tracks")
    clips = relationship("TimelineClip", back_populates="track", cascade="all, delete-orphan")


class TimelineClip(Base):
    __tablename__ = "timeline_clips"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    track_id = Column(Integer, ForeignKey("timeline_tracks.id"), nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True, index=True)
    storyboard_id = Column(Integer, ForeignKey("storyboards.id"), nullable=True, index=True)
    name = Column(String(200), nullable=True)

    start_time = Column(Integer, nullable=False)
    end_time = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)

    trim_start = Column(Integer, nullable=True)
    trim_end = Column(Integer, nullable=True)
    speed = Column(Float, default=1.0)

    volume = Column(Integer, nullable=True)
    is_muted = Column(Boolean, default=False)
    fade_in = Column(Integer, nullable=True)
    fade_out = Column(Integer, nullable=True)

    transition_in_id = Column(Integer, ForeignKey("clip_transitions.id"), nullable=True, index=True)
    transition_out_id = Column(Integer, ForeignKey("clip_transitions.id"), nullable=True, index=True)

    # Relationships
    track = relationship("TimelineTrack", back_populates="clips")
    asset = relationship("Asset")
    storyboard = relationship("Storyboard")
    in_transition = relationship("ClipTransition", foreign_keys=[transition_in_id])
    out_transition = relationship("ClipTransition", foreign_keys=[transition_out_id])
    effects = relationship("ClipEffect", back_populates="clip", cascade="all, delete-orphan")


class TransitionType(str, enum.Enum):
    FADE = "fade"
    CROSSFADE = "crossfade"
    SLIDE = "slide"
    WIPE = "wipe"
    ZOOM = "zoom"
    DISSOLVE = "dissolve"


class ClipTransition(Base):
    __tablename__ = "clip_transitions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    type = Column(String(50), nullable=False)
    duration = Column(Integer, default=500, nullable=False)
    easing = Column(String(50), nullable=True)
    config = Column(JSON, nullable=True)


class EffectType(str, enum.Enum):
    FILTER = "filter"
    COLOR = "color"
    BLUR = "blur"
    BRIGHTNESS = "brightness"
    CONTRAST = "contrast"
    SATURATION = "saturation"


class ClipEffect(Base):
    __tablename__ = "clip_effects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    clip_id = Column(Integer, ForeignKey("timeline_clips.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    is_enabled = Column(Boolean, default=True)
    order = Column(Integer, default=0)
    config = Column(JSON, nullable=True)

    # Relationships
    clip = relationship("TimelineClip", back_populates="effects")
