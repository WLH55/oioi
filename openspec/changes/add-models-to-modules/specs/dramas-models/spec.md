# 剧本模块模型规范

## 概述

定义剧本相关的 SQLAlchemy 模型。

## 对应数据库表

- `dramas`

## 模型定义

### Drama

剧本模型，项目的顶层实体。

```python
class Drama(Base):
    """剧本"""
    __tablename__ = "dramas"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = Column(String, nullable=False)
    description: Mapped[str] = Column(Text)
    genre: Mapped[str] = Column(String)
    style: Mapped[str] = Column(String, default="realistic")  # 风格
    total_episodes: Mapped[int] = Column(Integer, default=1)  # 总集数
    total_duration: Mapped[int] = Column(Integer, default=0)  # 总时长(秒)
    status: Mapped[str] = Column(String, default="draft")  # draft, in_progress, completed
    thumbnail: Mapped[str] = Column(String)
    tags: Mapped[str] = Column(Text)  # JSON 存储
    metadata: Mapped[str] = Column(Text)  # JSON 存储
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime] = Column(DateTime, nullable=True)
```

## 关系

- `Drama` → 多个 `Episode` (一对多)
- `Drama` → 多个 `Character` (一对多)
- `Drama` → 多个 `Scene` (一对多)
- `Drama` → 多个 `Asset` (一对多)

## 文件位置

```
src/dramas/
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
# src/dramas/__init__.py
from src.dramas.models import Drama

__all__ = ["Drama"]
```
