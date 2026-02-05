# 时间线模块模型规范

## 概述

定义时间线相关的 SQLAlchemy 模型，包括时间线、轨道、片段、转场、效果等。

## 对应数据库表

- `timelines`
- `timeline_tracks`
- `timeline_clips`
- `clip_transitions`
- `clip_effects`

## 模型定义

### Timeline

时间线模型，属于特定剧本或分集。

```python
class Timeline(Base):
    """时间线"""
    __tablename__ = "timelines"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    drama_id: Mapped[int] = Column(Integer, nullable=False)
    episode_id: Mapped[int] = Column(Integer, nullable=True)
    name: Mapped[str] = Column(String, nullable=False)
    description: Mapped[str] = Column(Text)
    duration: Mapped[int] = Column(Integer, default=0)  # 总时长(秒)
    fps: Mapped[int] = Column(Integer, default=30)
    resolution: Mapped[str] = Column(String)
    status: Mapped[str] = Column(String, default="draft")  # draft, editing, completed, exporting
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime] = Column(DateTime, nullable=True)
```

### TimelineTrack

时间线轨道模型。

```python
class TimelineTrack(Base):
    """时间线轨道"""
    __tablename__ = "timeline_tracks"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    timeline_id: Mapped[int] = Column(Integer, nullable=False)
    name: Mapped[str] = Column(String, nullable=False)
    type: Mapped[str] = Column(String, nullable=False)  # video, audio, text
    track_order: Mapped[int] = Column(Integer, default=0)
    is_locked: Mapped[int] = Column(Integer, default=0)
    is_muted: Mapped[int] = Column(Integer, default=0)
    volume: Mapped[int] = Column(Integer, default=100)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime] = Column(DateTime, nullable=True)
```

### TimelineClip

时间线片段模型。

```python
class TimelineClip(Base):
    """时间线片段"""
    __tablename__ = "timeline_clips"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    track_id: Mapped[int] = Column(Integer, nullable=False)
    asset_id: Mapped[int] = Column(Integer, nullable=True)
    storyboard_id: Mapped[int] = Column(Integer, nullable=True)
    name: Mapped[str] = Column(String)
    start_time: Mapped[int] = Column(Integer, nullable=False)  # 开始时间(毫秒)
    end_time: Mapped[int] = Column(Integer, nullable=False)  # 结束时间(毫秒)
    duration: Mapped[int] = Column(Integer, nullable=False)  # 时长(毫秒)
    trim_start: Mapped[int] = Column(Integer, nullable=True)  # 裁剪开始(毫秒)
    trim_end: Mapped[int] = Column(Integer, nullable=True)  # 裁剪结束(毫秒)
    speed: Mapped[float] = Column(Float, default=1.0)
    volume: Mapped[int] = Column(Integer, nullable=True)
    is_muted: Mapped[int] = Column(Integer, default=0)
    fade_in: Mapped[int] = Column(Integer, nullable=True)  # 淡入时长(毫秒)
    fade_out: Mapped[int] = Column(Integer, nullable=True)  # 淡出时长(毫秒)
    transition_in_id: Mapped[int] = Column(Integer, nullable=True)
    transition_out_id: Mapped[int] = Column(Integer, nullable=True)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime] = Column(DateTime, nullable=True)
```

### ClipTransition

片段转场模型。

```python
class ClipTransition(Base):
    """片段转场"""
    __tablename__ = "clip_transitions"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = Column(String, nullable=False)  # fade, crossfade, slide, wipe, zoom, dissolve
    duration: Mapped[int] = Column(Integer, default=500)  # 转场时长(毫秒)
    easing: Mapped[str] = Column(String)
    config: Mapped[str] = Column(Text)  # JSON
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime] = Column(DateTime, nullable=True)
```

### ClipEffect

片段效果模型。

```python
class ClipEffect(Base):
    """片段效果"""
    __tablename__ = "clip_effects"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    clip_id: Mapped[int] = Column(Integer, nullable=False)
    type: Mapped[str] = Column(String, nullable=False)  # filter, color, blur, brightness, contrast, saturation
    name: Mapped[str] = Column(String)
    is_enabled: Mapped[int] = Column(Integer, default=1)
    effect_order: Mapped[int] = Column(Integer, default=0)
    config: Mapped[str] = Column(Text)  # JSON
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime] = Column(DateTime, nullable=True)
```

## 关系

- `Timeline` → 属于 `Drama` (多对一)
- `Timeline` → 多个 `TimelineTrack` (一对多)
- `TimelineTrack` → 多个 `TimelineClip` (一对多)
- `TimelineClip` → 多个 `ClipEffect` (一对多)
- `TimelineClip` → 引用 `ClipTransition` (转场)

## 文件位置

```
src/scenes/  # timelines 模块在 scenes 目录下
├── __init__.py
├── router.py
├── service.py
├── schemas.py
├── dependencies.py
├── exceptions.py
├── tasks.py
└── models.py  # <-- 新增 Timeline, TimelineTrack, TimelineClip, ClipTransition, ClipEffect
```

## 导出

```python
# src/scenes/__init__.py
from src.scenes.models import (
    Timeline, TimelineTrack, TimelineClip, ClipTransition, ClipEffect
)

__all__ = ["Timeline", "TimelineTrack", "TimelineClip", "ClipTransition", "ClipEffect"]
```
