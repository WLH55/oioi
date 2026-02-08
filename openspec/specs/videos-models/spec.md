# 视频生成模块模型规范

## 概述

定义视频生成记录相关的 SQLAlchemy 模型。

## 对应数据库表

- `video_generations`

## 模型定义

### VideoGeneration

视频生成记录模型。

```python
class VideoGeneration(Base):
    """视频生成记录"""
    __tablename__ = "video_generations"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    storyboard_id: Mapped[int] = Column(Integer, nullable=True)
    drama_id: Mapped[int] = Column(Integer, nullable=False)
    provider: Mapped[str] = Column(String, nullable=False)  # runway, pika, doubao, openai
    prompt: Mapped[str] = Column(Text, nullable=False)
    model: Mapped[str] = Column(String)
    image_gen_id: Mapped[int] = Column(Integer)
    image_url: Mapped[str] = Column(String)
    first_frame_url: Mapped[str] = Column(String)
    duration: Mapped[float] = Column(Float)  # 时长(秒)
    fps: Mapped[int] = Column(Integer)
    resolution: Mapped[str] = Column(String)
    aspect_ratio: Mapped[str] = Column(String)
    style: Mapped[str] = Column(String)
    motion_level: Mapped[int] = Column(Integer)
    camera_motion: Mapped[str] = Column(String)
    seed: Mapped[int] = Column(Integer)
    video_url: Mapped[str] = Column(String)
    minio_url: Mapped[str] = Column(String)
    local_path: Mapped[str] = Column(String)
    status: Mapped[str] = Column(String, default="pending")  # pending, processing, completed, failed
    task_id: Mapped[str] = Column(String)
    error_msg: Mapped[str] = Column(Text)
    completed_at: Mapped[datetime] = Column(DateTime, nullable=True)
    width: Mapped[int] = Column(Integer)
    height: Mapped[int] = Column(Integer)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime] = Column(DateTime, nullable=True)
```

## 关系

- `VideoGeneration` → 属于 `Storyboard` (多对一)
- `VideoGeneration` → 属于 `Drama` (多对一)
- `VideoGeneration` → 属于 `ImageGeneration` (多对一)

## 文件位置

```
src/videos/
├── __init__.py
├── router.py
├── service.py
├── schemas.py
├── dependencies.py
├── exceptions.py
└── models.py  # <-- 新增
```

## 导出

```python
# src/videos/__init__.py
from src.videos.models import VideoGeneration

__all__ = ["VideoGeneration"]
```
