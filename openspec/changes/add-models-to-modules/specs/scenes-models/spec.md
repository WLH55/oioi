# 场景模块模型规范

## 概述

定义场景相关的 SQLAlchemy 模型。

## 对应数据库表

- `scenes`

## 模型定义

### Scene

场景模型，属于特定剧本。

```python
class Scene(Base):
    """场景"""
    __tablename__ = "scenes"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    drama_id: Mapped[int] = Column(Integer, nullable=False)
    location: Mapped[str] = Column(String, nullable=False)  # 场景地点
    time: Mapped[str] = Column(String, nullable=False)  # 时间(白天/夜晚)
    prompt: Mapped[str] = Column(String, nullable=False)  # AI 生成提示词
    storyboard_count: Mapped[int] = Column(Integer, default=1)
    image_url: Mapped[str] = Column(String)
    status: Mapped[str] = Column(String, default="pending")  # pending, generated, failed
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime] = Column(DateTime, nullable=True)
```

## 关系

- `Scene` → 属于 `Drama` (多对一)
- `Scene` → 多个 `Storyboard` (一对多)

## 文件位置

```
src/scenes/
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
# src/scenes/__init__.py
from src.scenes.models import Scene

__all__ = ["Scene"]
```
