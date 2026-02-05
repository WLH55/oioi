"""
素材库模块数据库模型

定义素材资源管理相关的 SQLAlchemy 模型。
"""
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Text, Float
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Asset(Base):
    """素材资源"""
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    drama_id: Mapped[int] = mapped_column(Integer, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String, nullable=False)  # image, video, audio
    category: Mapped[str] = mapped_column(String, nullable=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    thumbnail_url: Mapped[str] = mapped_column(String, nullable=True)
    local_path: Mapped[str] = mapped_column(String, nullable=True)
    file_size: Mapped[int] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str] = mapped_column(String, nullable=True)
    width: Mapped[int] = mapped_column(Integer, nullable=True)
    height: Mapped[int] = mapped_column(Integer, nullable=True)
    duration: Mapped[float] = mapped_column(Float, nullable=True)  # 秒
    format: Mapped[str] = mapped_column(String, nullable=True)
    image_gen_id: Mapped[int] = mapped_column(Integer, nullable=True)
    video_gen_id: Mapped[int] = mapped_column(Integer, nullable=True)
    is_favorite: Mapped[int] = mapped_column(Integer, default=0)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class AssetTag(Base):
    """素材标签"""
    __tablename__ = "asset_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    color: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class AssetCollection(Base):
    """素材集合"""
    __tablename__ = "asset_collections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    drama_id: Mapped[int] = mapped_column(Integer, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class AssetTagRelation(Base):
    """素材-标签关联"""
    __tablename__ = "asset_tag_relations"

    asset_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_tag_id: Mapped[int] = mapped_column(Integer, primary_key=True)


class AssetCollectionRelation(Base):
    """素材-集合关联"""
    __tablename__ = "asset_collection_relations"

    asset_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_collection_id: Mapped[int] = mapped_column(Integer, primary_key=True)
