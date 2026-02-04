"""
角色库 API 测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_list_character_library_empty(client: AsyncClient):
    """测试获取空的角色库列表"""
    response = await client.get("/api/v1/character-library/list")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["total"] == 0
    assert data["data"]["items"] == []


@pytest.mark.asyncio
async def test_create_library_item(client: AsyncClient):
    """测试创建角色库项"""
    request_data = {
        "name": "测试角色",
        "category": "主角",
        "image_url": "https://example.com/test.jpg",
        "description": "这是一个测试角色",
        "tags": "勇敢,善良",
        "source_type": "generated"
    }

    response = await client.post("/api/v1/character-library/create", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["name"] == "测试角色"
    assert data["data"]["category"] == "主角"


@pytest.mark.asyncio
async def test_create_library_item_validation_error(client: AsyncClient):
    """测试创建角色库项 - 验证错误"""
    # 缺少必填字段
    request_data = {
        "name": "测试角色",
        # 缺少 image_url
    }

    response = await client.post("/api/v1/character-library/create", json=request_data)

    assert response.status_code == 422  # Pydantic 验证错误


@pytest.mark.asyncio
async def test_get_library_item(client: AsyncClient, db_session: AsyncSession):
    """测试获取角色库详情"""
    # 先创建一个角色库项
    from src.character_library.models import CharacterLibrary
    from src.character_library.service import CharacterLibraryService

    service = CharacterLibraryService(db_session)
    item = await service.create(
        {
            "name": "详情测试角色",
            "image_url": "https://example.com/detail.jpg",
        }
    )

    response = await client.get(f"/api/v1/character-library/info?item_id={item.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["id"] == item.id
    assert data["data"]["name"] == "详情测试角色"


@pytest.mark.asyncio
async def test_get_library_item_not_found(client: AsyncClient):
    """测试获取不存在的角色库项"""
    response = await client.get("/api/v1/character-library/info?item_id=99999")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] != 200  # 应该返回错误码
    assert "不存在" in data["message"]


@pytest.mark.asyncio
async def test_update_library_item(client: AsyncClient, db_session: AsyncSession):
    """测试更新角色库项"""
    from src.character_library.models import CharacterLibrary
    from src.character_library.service import CharacterLibraryService

    service = CharacterLibraryService(db_session)
    item = await service.create(
        {
            "name": "更新前",
            "image_url": "https://example.com/before.jpg",
        }
    )

    update_data = {
        "name": "更新后",
        "description": "已更新描述",
    }

    response = await client.post(
        f"/api/v1/character-library/update?item_id={item.id}",
        json=update_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["name"] == "更新后"
    assert data["data"]["description"] == "已更新描述"


@pytest.mark.asyncio
async def test_delete_library_item(client: AsyncClient, db_session: AsyncSession):
    """测试删除角色库项"""
    from src.character_library.service import CharacterLibraryService

    service = CharacterLibraryService(db_session)
    item = await service.create(
        {
            "name": "待删除",
            "image_url": "https://example.com/delete.jpg",
        }
    )

    response = await client.post(f"/api/v1/character-library/delete?item_id={item.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

    # 验证删除后无法找到
    get_response = await client.get(f"/api/v1/character-library/info?item_id={item.id}")
    assert get_response.json()["code"] != 200


@pytest.mark.asyncio
async def test_list_character_library_with_filters(client: AsyncClient, db_session: AsyncSession):
    """测试带过滤条件的角色库列表"""
    from src.character_library.service import CharacterLibraryService

    service = CharacterLibraryService(db_session)

    # 创建多个角色库项
    await service.create({
        "name": "主角1",
        "category": "主角",
        "image_url": "https://example.com/main1.jpg",
    })
    await service.create({
        "name": "配角1",
        "category": "配角",
        "image_url": "https://example.com/side1.jpg",
    })
    await service.create({
        "name": "主角2",
        "category": "主角",
        "image_url": "https://example.com/main2.jpg",
    })

    # 测试分类过滤
    response = await client.get("/api/v1/character-library/list?category=主角")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["total"] == 2

    # 测试关键词搜索
    response = await client.get("/api/v1/character-library/list?keyword=配角")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["total"] == 1


@pytest.mark.asyncio
async def test_add_character_to_library_no_image(client: AsyncClient, db_session: AsyncSession):
    """测试将没有图片的角色添加到角色库"""
    from app.models.drama import Drama, Character
    from src.character_library.service import CharacterLibraryService

    service = CharacterLibraryService(db_session)

    # 创建一个剧目和没有图片的角色
    drama = Drama(title="测试剧目")
    db_session.add(drama)
    await db_session.flush()

    character = Character(
        drama_id=drama.id,
        name="无图角色",
        # 没有 image_url
    )
    db_session.add(character)
    await db_session.commit()

    response = await client.post(
        f"/api/v1/character-library/characters/add-to-library?character_id={character.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] != 200  # 应该返回错误
    assert "没有图片" in data["message"]
