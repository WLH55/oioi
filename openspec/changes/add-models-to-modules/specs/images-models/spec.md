# 图片生成模块模型规范

## 概述

定义图片生成记录相关的 SQLAlchemy 模型。

## 对应数据库表

- `image_generations`

## 模型定义

### ImageGeneration

图片生成记录模型。

```python
class ImageGeneration(Base):
    """图片生成记录"""
    __tablename__ = "image_generations"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    storyboard_id: Mapped[int] = Column(Integer, nullable=True)
    drama_id: Mapped[int] = Column(Integer, nullable=False)
    provider: Mapped[str] = Column(String, nullable=False)  # openai, midjourney, stable_diffusion
    prompt: Mapped[str] = Column(Text, nullable=False)
    negative_prompt: Mapped[str] = Column(Text)
    model: Mapped[str] = Column(String)
    size: Mapped[str] = Column(String)  # 如 1024x1024
    quality: Mapped[str] = Column(String)
    style: Mapped[str] = Column(String)
    steps: Mapped[int] = Column(Integer)
    cfg_scale: Mapped[float] = Column(Float)
    seed: Mapped[int] = Column(Integer)
    image_url: Mapped[str] = Column(String)
    minio_url: Mapped[str] = Column(String)
    local_path: Mapped[str] = Column(String)
    status: Mapped[str] = Column(String, default="pending")  # pending, processing, completed, failed
    task_id: Mapped[str] = Column(String)
    error_msg: Mapped[str] = Column(Text)
    width: Mapped[int] = Column(Integer)
    height: Mapped[int] = Column(Integer)
    reference_images: Mapped[str] = Column(Text)  # JSON
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at: Mapped[datetime] = Column(DateTime, nullable=True)
    deleted_at: Mapped[datetime] = Column(DateTime, nullable=True)
```

## 关系

- `ImageGeneration` → 属于 `Storyboard` (多对一)
- `ImageGeneration` → 属于 `Drama` (多对一)
- `ImageGeneration` → 多个 `Asset` (一对多)

## 文件位置

```
src/images/
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
# src/images/__init__.py
from src.images.models import ImageGeneration

__all__ = ["ImageGeneration"]
```
