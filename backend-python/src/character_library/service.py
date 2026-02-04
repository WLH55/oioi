"""
角色库业务逻辑层

处理角色库的 CRUD 操作和业务逻辑。
"""
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .models import CharacterLibrary
from .schemas import CharacterLibraryCreate, CharacterLibraryUpdate
from .exceptions import CharacterLibraryNotFound
from app.models.drama import Character


class CharacterLibraryService:
    """角色库服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        source_type: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> tuple[List[CharacterLibrary], int]:
        """
        获取角色库列表

        Args:
            skip: 跳过数量
            limit: 限制数量
            category: 分类过滤
            source_type: 来源类型过滤
            keyword: 关键词搜索

        Returns:
            (角色库列表, 总数)
        """
        query = select(CharacterLibrary)

        # 应用过滤条件
        if category:
            query = query.where(CharacterLibrary.category == category)
        if source_type:
            query = query.where(CharacterLibrary.source_type == source_type)
        if keyword:
            query = query.where(
                (CharacterLibrary.name.contains(keyword)) |
                (CharacterLibrary.description.contains(keyword))
            )

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # 获取分页结果
        query = query.offset(skip).limit(limit).order_by(CharacterLibrary.created_at.desc())
        result = await self.db.execute(query)
        items = result.scalars().all()

        return list(items), total

    async def get_by_id(self, item_id: int) -> CharacterLibrary:
        """
        根据 ID 获取角色库项

        Args:
            item_id: 角色 ID

        Returns:
            角色库项

        Raises:
            CharacterLibraryNotFound: 角色库项不存在
        """
        result = await self.db.execute(
            select(CharacterLibrary).where(CharacterLibrary.id == item_id)
        )
        item = result.scalar_one_or_none()

        if not item:
            raise CharacterLibraryNotFound(item_id)

        return item

    async def create(self, data: CharacterLibraryCreate) -> CharacterLibrary:
        """
        创建角色库项

        Args:
            data: 创建数据

        Returns:
            创建的角色库项
        """
        db_item = CharacterLibrary(**data.model_dump())
        self.db.add(db_item)
        await self.db.commit()
        await self.db.refresh(db_item)
        return db_item

    async def update(self, item_id: int, data: CharacterLibraryUpdate) -> CharacterLibrary:
        """
        更新角色库项

        Args:
            item_id: 角色 ID
            data: 更新数据

        Returns:
            更新后的角色库项

        Raises:
            CharacterLibraryNotFound: 角色库项不存在
        """
        item = await self.get_by_id(item_id)

        # 更新字段
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)

        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def delete(self, item_id: int) -> None:
        """
        删除角色库项

        Args:
            item_id: 角色 ID

        Raises:
            CharacterLibraryNotFound: 角色库项不存在
        """
        item = await self.get_by_id(item_id)
        await self.db.delete(item)
        await self.db.commit()

    async def get_character_by_id(self, character_id: int) -> Character:
        """
        获取 Drama 模块的角色

        Args:
            character_id: 角色 ID

        Returns:
            角色对象

        Raises:
            CharacterNotFound: 角色不存在
        """
        from .exceptions import CharacterNotFound

        result = await self.db.execute(
            select(Character).where(Character.id == character_id)
        )
        character = result.scalar_one_or_none()

        if not character:
            raise CharacterNotFound(character_id)

        return character

    async def update_character_image(
        self, character_id: int, image_url: str
    ) -> Character:
        """
        更新角色图片

        Args:
            character_id: 角色 ID
            image_url: 图片 URL

        Returns:
            更新后的角色
        """
        character = await self.get_character_by_id(character_id)
        character.image_url = image_url
        await self.db.commit()
        await self.db.refresh(character)
        return character

    async def apply_library_image_to_character(
        self, character_id: int, library_item_id: int
    ) -> Dict[str, Any]:
        """
        将角色库图片应用到角色

        Args:
            character_id: 角色 ID
            library_item_id: 角色库项 ID

        Returns:
            应用结果
        """
        # 获取角色和角色库项
        character = await self.get_character_by_id(character_id)
        library_item = await self.get_by_id(library_item_id)

        # 应用图片
        character.image_url = library_item.image_url
        await self.db.commit()
        await self.db.refresh(character)

        return {
            "character_id": character_id,
            "library_item_id": library_item_id,
            "image_url": library_item.image_url,
        }

    async def add_character_to_library(
        self,
        character_id: int,
        name: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        将角色添加到角色库

        Args:
            character_id: 角色 ID
            name: 自定义名称
            category: 分类

        Returns:
            添加结果
        """
        from .exceptions import CharacterHasNoImage

        character = await self.get_character_by_id(character_id)

        if not character.image_url:
            raise CharacterHasNoImage()

        # 创建角色库项
        library_item = CharacterLibrary(
            name=name or character.name,
            category=category,
            image_url=character.image_url,
            description=character.description,
            source_type="character",
        )

        self.db.add(library_item)
        await self.db.commit()
        await self.db.refresh(library_item)

        return {
            "character_id": character_id,
            "library_item_id": library_item.id,
        }

    async def update_character(
        self,
        character_id: int,
        name: Optional[str] = None,
        role: Optional[str] = None,
        description: Optional[str] = None,
        appearance: Optional[str] = None,
        personality: Optional[str] = None,
        voice_style: Optional[str] = None,
    ) -> Character:
        """
        更新角色信息

        Args:
            character_id: 角色 ID
            name: 名称
            role: 角色
            description: 描述
            appearance: 外貌
            personality: 性格
            voice_style: 声音风格

        Returns:
            更新后的角色
        """
        character = await self.get_character_by_id(character_id)

        if name is not None:
            character.name = name
        if role is not None:
            character.role = role
        if description is not None:
            character.description = description
        if appearance is not None:
            character.appearance = appearance
        if personality is not None:
            character.personality = personality
        if voice_style is not None:
            character.voice_style = voice_style

        await self.db.commit()
        await self.db.refresh(character)
        return character

    async def delete_character(self, character_id: int) -> None:
        """
        删除角色

        Args:
            character_id: 角色 ID
        """
        character = await self.get_character_by_id(character_id)
        await self.db.delete(character)
        await self.db.commit()

    async def batch_generate_character_images(
        self, character_ids: List[int]
    ) -> List[Dict[str, Any]]:
        """
        批量生成角色图片

        Args:
            character_ids: 角色 ID 列表

        Returns:
            生成任务列表
        """
        # 验证所有角色存在
        result = await self.db.execute(
            select(Character).where(Character.id.in_(character_ids))
        )
        characters = result.scalars().all()

        if len(characters) != len(character_ids):
            from .exceptions import CharacterNotFound
            found_ids = {c.id for c in characters}
            missing_ids = set(character_ids) - found_ids
            raise CharacterNotFound(missing_ids.pop())

        # 创建生成任务（简化实现）
        task_ids = []
        for character in characters:
            task_id = f"char_img_gen_{character.id}_{hash(str(character.id))}"
            task_ids.append({
                "character_id": character.id,
                "task_id": task_id,
            })

        return task_ids

    async def generate_character_image(
        self, character_id: int
    ) -> Dict[str, Any]:
        """
        生成角色图片

        Args:
            character_id: 角色 ID

        Returns:
            生成任务信息
        """
        character = await self.get_character_by_id(character_id)

        # 简化实现，实际应调用 AI 服务
        task_id = f"char_img_gen_{character_id}"

        return {
            "character_id": character_id,
            "task_id": task_id,
            "status": "pending",
        }
