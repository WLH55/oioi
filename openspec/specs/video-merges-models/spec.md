# 视频合成模块模型规范

## 概述

定义视频合成记录相关的 SQLAlchemy 模型。

## 对应数据库表

- `video_merges`

## 模型定义

### VideoMerge

视频合成记录模型，用于合并多个视频片段。

```python
class VideoMerge(Base):
    """视频合成记录"""
    __tablename__ = "video_merges"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    episode_id: Mapped[int] = Column(Integer, nullable=False)
    drama_id: Mapped[int] = Column(Integer, nullable=False)
    title: Mapped[str] = Column(String)
    provider: Mapped[str] = Column(String, nullable=False)
    model: Mapped[str] = Column(String)
    status: Mapped[str] = Column(String, default="pending")  # pending, processing, completed, failed
    scenes: Mapped[str] = Column(Text, nullable=False)  # JSON - 场景片段列表
    merged_url: Mapped[str] = Column(String)
    duration: Mapped[int] = Column(Integer)  # 总时长(秒)
    task_id: Mapped[str] = Column(String)
    error_msg: Mapped[str] = Column(Text)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime] = Column(DateTime, nullable=True)
    deleted_at: Mapped[datetime] = Column(DateTime, nullable=True)
```

## 关系

- `VideoMerge` → 属于 `Episode` (多对一)
- `VideoMerge` → 属于 `Drama` (多对一)

## 文件位置

```
src/video_merges/
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
# src/video_merges/__init__.py
from src.video_merges.models import VideoMerge

__all__ = ["VideoMerge"]
```
