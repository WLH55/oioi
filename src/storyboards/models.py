"""
故事板模块数据库模型

定义故事板相关的 SQLAlchemy 模型。
"""
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Storyboard(Base):
    """故事板"""
    __tablename__ = "storyboards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    episode_id: Mapped[int] = mapped_column(Integer, nullable=False)
    scene_id: Mapped[int] = mapped_column(Integer, nullable=True)
    storyboard_number: Mapped[int] = mapped_column(Integer, nullable=False)  # 分镜序号
    title: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    location: Mapped[str] = mapped_column(String, nullable=True)  # 场景地点
    time: Mapped[str] = mapped_column(String, nullable=True)  # 时间
    duration: Mapped[int] = mapped_column(Integer, default=0)  # 时长(秒)
    dialogue: Mapped[str] = mapped_column(Text, nullable=True)  # 对话
    action: Mapped[str] = mapped_column(Text, nullable=True)  # 动作
    atmosphere: Mapped[str] = mapped_column(String, nullable=True)  # 氛围
    image_prompt: Mapped[str] = mapped_column(Text, nullable=True)  # 图片生成提示词
    video_prompt: Mapped[str] = mapped_column(Text, nullable=True)  # 视频生成提示词
    characters: Mapped[str] = mapped_column(Text, nullable=True)  # JSON - 角色信息
    composed_image: Mapped[str] = mapped_column(String, nullable=True)  # 合成后的图片URL
    video_url: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending")  # pending, processing, completed, failed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
