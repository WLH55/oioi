# 角色库模块模型规范

## 概述

定义角色库相关的 SQLAlchemy 模型，包括角色库和角色信息。

## 对应数据库表

- `character_libraries`
- `characters` (隶属于角色库)

## 模型定义

### CharacterLibrary

角色库模型，用于存储全局共享的角色信息。

```python
class CharacterLibrary(Base):
    """角色库"""
    __tablename__ = "character_libraries"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = Column(String, nullable=False)
    category: Mapped[str] = Column(String)
    image_url: Mapped[str] = Column(String, nullable=False)
    description: Mapped[str] = Column(String)
    tags: Mapped[str] = Column(Text)  # JSON
    source_type: Mapped[str] = Column(String, default="generated")  # generated, uploaded
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime] = Column(DateTime, nullable=True)
```

### Character

剧本角色模型，隶属于特定剧本。

```python
class Character(Base):
    """剧本角色"""
    __tablename__ = "characters"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    drama_id: Mapped[int] = Column(Integer, nullable=False)
    name: Mapped[str] = Column(String, nullable=False)
    role: Mapped[str] = Column(String)
    description: Mapped[str] = Column(String)
    appearance: Mapped[str] = Column(String)
    personality: Mapped[str] = Column(String)
    voice_style: Mapped[str] = Column(String)
    image_url: Mapped[str] = Column(String)
    reference_images: Mapped[str] = Column(Text)  # JSON
    seed_value: Mapped[str] = Column(String)
    sort_order: Mapped[int] = Column(Integer, default=0)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime] = Column(DateTime, nullable=True)
```

## 文件位置

```
src/character_library/
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
# src/character_library/__init__.py
from src.character_library.models import CharacterLibrary, Character

__all__ = ["CharacterLibrary", "Character"]
```
