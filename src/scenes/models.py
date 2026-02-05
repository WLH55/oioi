"""
场景模块数据库模型

定义场景和时间线相关的 SQLAlchemy 模型。
"""
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Scene(Base):
    """场景"""
    __tablename__ = "scenes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    drama_id: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)  # 场景地点
    time: Mapped[str] = mapped_column(String, nullable=False)  # 时间(白天/夜晚)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)  # AI 生成提示词
    storyboard_count: Mapped[int] = mapped_column(Integer, default=1)
    image_url: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending")  # pending, generated, failed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class Timeline(Base):
    """时间线"""
    __tablename__ = "timelines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    drama_id: Mapped[int] = mapped_column(Integer, nullable=False)
    episode_id: Mapped[int] = mapped_column(Integer, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    duration: Mapped[int] = mapped_column(Integer, default=0)  # 总时长(秒)
    fps: Mapped[int] = mapped_column(Integer, default=30)
    resolution: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="draft")  # draft, editing, completed, exporting
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class TimelineTrack(Base):
    """时间线轨道"""
    __tablename__ = "timeline_tracks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timeline_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)  # video, audio, text
    track_order: Mapped[int] = mapped_column(Integer, default=0)
    is_locked: Mapped[int] = mapped_column(Integer, default=0)
    is_muted: Mapped[int] = mapped_column(Integer, default=0)
    volume: Mapped[int] = mapped_column(Integer, default=100)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class TimelineClip(Base):
    """时间线片段"""
    __tablename__ = "timeline_clips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    track_id: Mapped[int] = mapped_column(Integer, nullable=False)
    asset_id: Mapped[int] = mapped_column(Integer, nullable=True)
    storyboard_id: Mapped[int] = mapped_column(Integer, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    start_time: Mapped[int] = mapped_column(Integer, nullable=False)  # 开始时间(毫秒)
    end_time: Mapped[int] = mapped_column(Integer, nullable=False)  # 结束时间(毫秒)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)  # 时长(毫秒)
    trim_start: Mapped[int] = mapped_column(Integer, nullable=True)  # 裁剪开始(毫秒)
    trim_end: Mapped[int] = mapped_column(Integer, nullable=True)  # 裁剪结束(毫秒)
    speed: Mapped[float] = mapped_column(Float, default=1.0)
    volume: Mapped[int] = mapped_column(Integer, nullable=True)
    is_muted: Mapped[int] = mapped_column(Integer, default=0)
    fade_in: Mapped[int] = mapped_column(Integer, nullable=True)  # 淡入时长(毫秒)
    fade_out: Mapped[int] = mapped_column(Integer, nullable=True)  # 淡出时长(毫秒)
    transition_in_id: Mapped[int] = mapped_column(Integer, nullable=True)
    transition_out_id: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class ClipTransition(Base):
    """片段转场"""
    __tablename__ = "clip_transitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String, nullable=False)  # fade, crossfade, slide, wipe, zoom, dissolve
    duration: Mapped[int] = mapped_column(Integer, default=500)  # 转场时长(毫秒)
    easing: Mapped[str] = mapped_column(String, nullable=True)
    config: Mapped[str] = mapped_column(Text, nullable=True)  # JSON
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class ClipEffect(Base):
    """片段效果"""
    __tablename__ = "clip_effects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clip_id: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)  # filter, color, blur, brightness, contrast, saturation
    name: Mapped[str] = mapped_column(String, nullable=True)
    is_enabled: Mapped[int] = mapped_column(Integer, default=1)
    effect_order: Mapped[int] = mapped_column(Integer, default=0)
    config: Mapped[str] = mapped_column(Text, nullable=True)  # JSON
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
