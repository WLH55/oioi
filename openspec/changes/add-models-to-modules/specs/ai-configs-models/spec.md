# AI 配置模块模型规范

## 概述

定义 AI 服务配置相关的 SQLAlchemy 模型，包括服务配置和提供商信息。

## 对应数据库表

- `ai_service_configs`
- `ai_service_providers`

## 模型定义

### AIServiceConfig

AI 服务配置模型，用于存储各 AI 服务提供商的 API 配置。

```python
class AIServiceConfig(Base):
    """AI 服务配置"""
    __tablename__ = "ai_service_configs"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    service_type: Mapped[str] = Column(String, nullable=False)  # text, image, video
    provider: Mapped[str] = Column(String)
    name: Mapped[str] = Column(String, nullable=False)
    base_url: Mapped[str] = Column(String, nullable=False)
    api_key: Mapped[str] = Column(String, nullable=False)
    model: Mapped[str] = Column(String)
    endpoint: Mapped[str] = Column(String)
    query_endpoint: Mapped[str] = Column(String)
    priority: Mapped[int] = Column(Integer, default=0)
    is_default: Mapped[int] = Column(Integer, default=0)
    is_active: Mapped[int] = Column(Integer, default=1)
    settings: Mapped[str] = Column(Text)  # JSON
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime] = Column(DateTime, nullable=True)
```

### AIServiceProvider

AI 服务提供商信息。

```python
class AIServiceProvider(Base):
    """AI 服务提供商"""
    __tablename__ = "ai_service_providers"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = Column(String, nullable=False, unique=True)
    display_name: Mapped[str] = Column(String, nullable=False)
    service_type: Mapped[str] = Column(String, nullable=False)  # text, image, video
    default_url: Mapped[str] = Column(String)
    description: Mapped[str] = Column(String)
    is_active: Mapped[int] = Column(Integer, default=1)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime] = Column(DateTime, nullable=True)
```

## 文件位置

```
src/ai_configs/
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
# src/ai_configs/__init__.py
from src.ai_configs.models import AIServiceConfig, AIServiceProvider

__all__ = ["AIServiceConfig", "AIServiceProvider"]
```
