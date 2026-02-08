# 素材库模块模型规范

## 概述

定义素材资源管理相关的 SQLAlchemy 模型，包括素材、标签、集合等。

## 对应数据库表

- `assets`
- `asset_tags`
- `asset_collections`
- `asset_tag_relations`
- `asset_collection_relations`

## 模型定义

### Asset

素材资源模型，用于存储图片、视频、音频等素材。

```python
class Asset(Base):
    """素材资源"""
    __tablename__ = "assets"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    drama_id: Mapped[int] = Column(Integer, nullable=True)
    name: Mapped[str] = Column(String, nullable=False)
    description: Mapped[str] = Column(String)
    type: Mapped[str] = Column(String, nullable=False)  # image, video, audio
    category: Mapped[str] = Column(String)
    url: Mapped[str] = Column(String, nullable=False)
    thumbnail_url: Mapped[str] = Column(String)
    local_path: Mapped[str] = Column(String)
    file_size: Mapped[int] = Column(Integer)
    mime_type: Mapped[str] = Column(String)
    width: Mapped[int] = Column(Integer)
    height: Mapped[int] = Column(Integer)
    duration: Mapped[float] = Column(Float)  # 秒
    format: Mapped[str] = Column(String)
    image_gen_id: Mapped[int] = Column(Integer)
    video_gen_id: Mapped[int] = Column(Integer)
    is_favorite: Mapped[int] = Column(Integer, default=0)
    view_count: Mapped[int] = Column(Integer, default=0)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime] = Column(DateTime, nullable=True)
```

### AssetTag

素材标签模型。

```python
class AssetTag(Base):
    """素材标签"""
    __tablename__ = "asset_tags"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = Column(String, nullable=False)
    color: Mapped[str] = Column(String)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime] = Column(DateTime, nullable=True)
```

### AssetCollection

素材集合模型，用于组织多个素材。

```python
class AssetCollection(Base):
    """素材集合"""
    __tablename__ = "asset_collections"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    drama_id: Mapped[int] = Column(Integer, nullable=True)
    name: Mapped[str] = Column(String, nullable=False)
    description: Mapped[str] = Column(String)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime] = Column(DateTime, nullable=True)
```

### AssetTagRelation

素材与标签的多对多关系。

```python
class AssetTagRelation(Base):
    """素材-标签关联"""
    __tablename__ = "asset_tag_relations"

    asset_id: Mapped[int] = Column(Integer, primary_key=True)
    asset_tag_id: Mapped[int] = Column(Integer, primary_key=True)
```

### AssetCollectionRelation

素材与集合的多对多关系。

```python
class AssetCollectionRelation(Base):
    """素材-集合关联"""
    __tablename__ = "asset_collection_relations"

    asset_id: Mapped[int] = Column(Integer, primary_key=True)
    asset_collection_id: Mapped[int] = Column(Integer, primary_key=True)
```

## 文件位置

```
src/assets/
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
# src/assets/__init__.py
from src.assets.models import Asset, AssetTag, AssetCollection, AssetTagRelation, AssetCollectionRelation

__all__ = ["Asset", "AssetTag", "AssetCollection", "AssetTagRelation", "AssetCollectionRelation"]
```
