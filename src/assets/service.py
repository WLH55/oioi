"""
资源业务逻辑层

处理资源的 CRUD 操作和业务逻辑。
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.assets.models import Asset

from .exceptions import AssetNotFound
from .schemas import AssetCreate, AssetUpdate


class AssetService:
    """资源服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self,
        skip: int = 0,
        limit: int = 100,
        drama_id: int | None = None,
        episode_id: int | None = None,
        asset_type: str | None = None,
        category: str | None = None,
    ) -> tuple[list[Asset], int]:
        """
        获取资源列表

        Args:
            skip: 跳过数量
            limit: 限制数量
            drama_id: 剧目 ID 过滤
            episode_id: 集数 ID 过滤
            asset_type: 资源类型过滤
            category: 分类过滤

        Returns:
            (资源列表, 总数)
        """
        query = select(Asset)

        # 应用过滤条件
        if drama_id:
            query = query.where(Asset.drama_id == drama_id)
        if episode_id:
            query = query.where(Asset.episode_id == episode_id)
        if asset_type:
            query = query.where(Asset.type == asset_type)
        if category:
            query = query.where(Asset.category == category)

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # 获取分页结果
        query = query.offset(skip).limit(limit).order_by(Asset.created_at.desc())
        result = await self.db.execute(query)
        items = result.scalars().all()

        return list(items), total

    async def get_by_id(self, asset_id: int) -> Asset:
        """
        根据 ID 获取资源

        Args:
            asset_id: 资源 ID

        Returns:
            资源对象

        Raises:
            AssetNotFound: 资源不存在
        """
        result = await self.db.execute(
            select(Asset).where(Asset.id == asset_id)
        )
        asset = result.scalar_one_or_none()

        if not asset:
            raise AssetNotFound(asset_id)

        # 增加浏览次数
        asset.view_count += 1
        await self.db.commit()

        return asset

    async def create(self, data: AssetCreate) -> Asset:
        """
        创建资源

        Args:
            data: 创建数据

        Returns:
            创建的资源对象
        """
        db_asset = Asset(**data.model_dump())
        self.db.add(db_asset)
        await self.db.commit()
        await self.db.refresh(db_asset)
        return db_asset

    async def update(self, asset_id: int, data: AssetUpdate) -> Asset:
        """
        更新资源

        Args:
            asset_id: 资源 ID
            data: 更新数据

        Returns:
            更新后的资源对象

        Raises:
            AssetNotFound: 资源不存在
        """
        asset = await self.get_by_id(asset_id)

        # 更新字段
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(asset, field, value)

        await self.db.commit()
        await self.db.refresh(asset)
        return asset

    async def delete(self, asset_id: int) -> None:
        """
        删除资源

        Args:
            asset_id: 资源 ID

        Raises:
            AssetNotFound: 资源不存在
        """
        asset = await self.get_by_id(asset_id)
        await self.db.delete(asset)
        await self.db.commit()

    async def import_from_image_gen(
        self,
        image_gen_id: int,
        name: str,
        description: str | None = None,
        category: str | None = None,
    ) -> Asset:
        """
        从图片生成记录导入资源

        Args:
            image_gen_id: 图片生成 ID
            name: 资源名称
            description: 描述
            category: 分类

        Returns:
            创建的资源对象
        """
        from src.images.models import ImageGeneration

        from .exceptions import GenerationHasNoUrl, ImageGenerationNotFound

        # 获取图片生成记录
        result = await self.db.execute(
            select(ImageGeneration).where(ImageGeneration.id == image_gen_id)
        )
        image_gen = result.scalar_one_or_none()

        if not image_gen:
            raise ImageGenerationNotFound(image_gen_id)

        if not image_gen.image_url:
            raise GenerationHasNoUrl("图片生成记录")

        # 创建资源
        asset = Asset(
            name=name,
            type=AssetType.IMAGE.value,
            url=image_gen.image_url,
            local_path=image_gen.local_path,
            width=image_gen.width,
            height=image_gen.height,
            description=description,
            category=category,
            drama_id=image_gen.drama_id,
            image_gen_id=image_gen.id
        )

        self.db.add(asset)
        await self.db.commit()
        await self.db.refresh(asset)
        return asset

    async def import_from_video_gen(
        self,
        video_gen_id: int,
        name: str,
        description: str | None = None,
        category: str | None = None,
    ) -> Asset:
        """
        从视频生成记录导入资源

        Args:
            video_gen_id: 视频生成 ID
            name: 资源名称
            description: 描述
            category: 分类

        Returns:
            创建的资源对象
        """
        from src.videos.models import VideoGeneration

        from .exceptions import GenerationHasNoUrl, VideoGenerationNotFound

        # 获取视频生成记录
        result = await self.db.execute(
            select(VideoGeneration).where(VideoGeneration.id == video_gen_id)
        )
        video_gen = result.scalar_one_or_none()

        if not video_gen:
            raise VideoGenerationNotFound(video_gen_id)

        if not video_gen.video_url:
            raise GenerationHasNoUrl("视频生成记录")

        # 创建资源
        asset = Asset(
            name=name,
            type=AssetType.VIDEO.value,
            url=video_gen.video_url,
            local_path=video_gen.local_path,
            width=video_gen.width,
            height=video_gen.height,
            duration=video_gen.duration,
            description=description,
            category=category,
            drama_id=video_gen.drama_id,
            video_gen_id=video_gen.id
        )

        self.db.add(asset)
        await self.db.commit()
        await self.db.refresh(asset)
        return asset
