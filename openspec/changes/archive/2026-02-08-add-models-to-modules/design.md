# 设计方案

## 1. 目录结构调整

```
src/
├── core/                    # 新增：核心模块
│   ├── __init__.py
│   ├── config.py           # 从 src/config.py 复制
│   └── schemas.py          # 从 src/schemas.py 复制
├── database.py             # 修改：定义 Base 和异步引擎
├── config.py               # 删除
├── schemas.py              # 删除
└── {模块}/                 # 业务模块
    ├── __init__.py
    ├── router.py
    ├── service.py
    ├── schemas.py
    ├── dependencies.py
    ├── exceptions.py
    └── models.py           # 新增：SQLAlchemy 模型
```

## 2. Base 类定义

```python
# src/database.py
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """SQLAlchemy 基础模型类"""
    pass
```

## 3. 模型命名规范

每个模型的 `__tablename__` 使用复数形式：
- `ai_configs`
- `assets`
- `dramas`
- `episodes`
- `scenes`
- `storyboards`
- `character_library`
- `tasks`
- `images`
- `videos`
- `audio`
- `video_merges`

## 4. 通用字段

所有模型包含以下通用字段：
- `id`: int, primary_key
- `created_at`: DateTime, default=datetime.utcnow
- `updated_at`: DateTime, default=datetime.utcnow, onupdate=datetime.utcnow

## 5. 导入路径变更

| 原路径 | 新路径 |
|--------|--------|
| `from app.core.config import settings` | `from src.core.config import settings` |
| `from src.config import settings` | `from src.core.config import settings` |
| `from src.schemas import ApiResponse` | `from src.core.schemas import ApiResponse` |
| `from app.core.database import Base` | `from src.database import Base` |
