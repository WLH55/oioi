# 分集模块模型规范

## 概述

定义剧本分集相关的 SQLAlchemy 模型。

## 对应数据库表

- `episodes`

## 模型定义

### Episode

分集模型，属于特定剧本。

```python
class Episode(Base):
    """剧本分集"""
    __tablename__ = "episodes"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    drama_id: Mapped[int] = Column(Integer, nullable=False)
    episode_number: Mapped[int] = Column(Integer, nullable=False)  # 集数序号
    title: Mapped[str] = Column(String, nullable=False)
    script_content: Mapped[str] = Column(Text)  # 剧本内容
    description: Mapped[str] = Column(Text)
    duration: Mapped[int] = Column(Integer, default=0)  # 时长(秒)
    status: Mapped[str] = Column(String, default="draft")
    video_url: Mapped[str] = Column(String)
    thumbnail: Mapped[str] = Column(String)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime] = Column(DateTime, nullable=True)
```

## 关系

- `Episode` → 属于 `Drama` (多对一)
- `Episode` → 多个 `Scene` (一对多)
- `Episode` → 多个 `Storyboard` (一对多)
- `Episode` → 多个 `VideoMerge` (一对多)

## 文件位置

```
src/episodes/
├── __init__.py
├── router.py
├── service.py
├── schemas.py
├── dependencies.py
├── exceptions.py
├── tasks.py
└── models.py  # <-- 新增
```

## 导出

```python
# src/episodes/__init__.py
from src.episodes.models import Episode

__all__ = ["Episode"]
```
