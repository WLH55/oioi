# 故事板模块模型规范

## 概述

定义故事板相关的 SQLAlchemy 模型。

## 对应数据库表

- `storyboards`

## 模型定义

### Storyboard

故事板模型，属于特定分集。

```python
class Storyboard(Base):
    """故事板"""
    __tablename__ = "storyboards"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    episode_id: Mapped[int] = Column(Integer, nullable=False)
    scene_id: Mapped[int] = Column(Integer, nullable=True)
    storyboard_number: Mapped[int] = Column(Integer, nullable=False)  # 分镜序号
    title: Mapped[str] = Column(String)
    description: Mapped[str] = Column(Text)
    location: Mapped[str] = Column(String)  # 场景地点
    time: Mapped[str] = Column(String)  # 时间
    duration: Mapped[int] = Column(Integer, default=0)  # 时长(秒)
    dialogue: Mapped[str] = Column(Text)  # 对话
    action: Mapped[str] = Column(Text)  # 动作
    atmosphere: Mapped[str] = Column(String)  # 氛围
    image_prompt: Mapped[str] = Column(Text)  # 图片生成提示词
    video_prompt: Mapped[str] = Column(Text)  # 视频生成提示词
    characters: Mapped[str] = Column(Text)  # JSON - 角色信息
    composed_image: Mapped[str] = Column(String)  # 合成后的图片URL
    video_url: Mapped[str] = Column(String)
    status: Mapped[str] = Column(String, default="pending")  # pending, processing, completed, failed
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime] = Column(DateTime, nullable=True)
```

## 关系

- `Storyboard` → 属于 `Episode` (多对一)
- `Storyboard` → 属于 `Scene` (多对一)
- `Storyboard` → 多个 `ImageGeneration` (一对多)
- `Storyboard` → 多个 `VideoGeneration` (一对多)

## 文件位置

```
src/storyboards/
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
# src/storyboards/__init__.py
from src.storyboards.models import Storyboard

__all__ = ["Storyboard"]
```
