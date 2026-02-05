"""
剧目 API 测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_list_dramas_empty(client: AsyncClient):
    """测试获取空的剧目列表"""
    response = await client.get("/api/v1/dramas/list")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["total"] == 0
    assert data["data"]["items"] == []


@pytest.mark.asyncio
async def test_create_drama(client: AsyncClient):
    """测试创建剧目"""
    request_data = {
        "title": "测试剧目",
        "description": "这是一个测试剧目",
        "genre": "科幻",
        "style": "realistic",
        "total_episodes": 10,
    }

    response = await client.post("/api/v1/dramas/create", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["title"] == "测试剧目"
    assert data["data"]["genre"] == "科幻"


@pytest.mark.asyncio
async def test_create_drama_validation_error(client: AsyncClient):
    """测试创建剧目 - 验证错误"""
    # 缺少必填字段
    request_data = {
        "description": "只有描述",
    }

    response = await client.post("/api/v1/dramas/create", json=request_data)

    assert response.status_code == 422  # Pydantic 验证错误


@pytest.mark.asyncio
async def test_get_drama(client: AsyncClient, db_session: AsyncSession):
    """测试获取剧目详情"""
    from app.models.drama import Drama
    from src.dramas.service import DramaService

    service = DramaService(db_session)
    drama = await service.create({
        "title": "详情测试剧目",
        "genre": "喜剧",
    })

    response = await client.get(f"/api/v1/dramas/info?drama_id={drama.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["id"] == drama.id
    assert data["data"]["title"] == "详情测试剧目"


@pytest.mark.asyncio
async def test_get_drama_not_found(client: AsyncClient):
    """测试获取不存在的剧目"""
    response = await client.get("/api/v1/dramas/info?drama_id=99999")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] != 200  # 应该返回错误码
    assert "不存在" in data["message"]


@pytest.mark.asyncio
async def test_update_drama(client: AsyncClient, db_session: AsyncSession):
    """测试更新剧目"""
    from src.dramas.service import DramaService

    service = DramaService(db_session)
    drama = await service.create({
        "title": "更新前",
        "genre": "动作",
    })

    update_data = {
        "title": "更新后",
        "description": "已更新描述",
    }

    response = await client.post(
        f"/api/v1/dramas/update?drama_id={drama.id}",
        json=update_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["title"] == "更新后"
    assert data["data"]["description"] == "已更新描述"


@pytest.mark.asyncio
async def test_delete_drama(client: AsyncClient, db_session: AsyncSession):
    """测试删除剧目"""
    from src.dramas.service import DramaService

    service = DramaService(db_session)
    drama = await service.create({
        "title": "待删除",
        "genre": "恐怖",
    })

    response = await client.post(f"/api/v1/dramas/delete?drama_id={drama.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["drama_id"] == drama.id

    # 验证删除后无法找到
    get_response = await client.get(f"/api/v1/dramas/info?drama_id={drama.id}")
    assert get_response.json()["code"] != 200


@pytest.mark.asyncio
async def test_list_episodes(client: AsyncClient, db_session: AsyncSession):
    """测试获取剧目集数列表"""
    from src.dramas.service import DramaService
    from app.models.drama import Episode

    service = DramaService(db_session)

    # 创建剧目
    drama = await service.create({
        "title": "测试剧集目",
        "genre": "科幻",
    })

    # 创建集数
    await service.create_episode(drama.id, {
        "episode_number": 1,
        "title": "第一集",
    })
    await service.create_episode(drama.id, {
        "episode_number": 2,
        "title": "第二集",
    })

    response = await client.get(f"/api/v1/dramas/episodes/list?drama_id={drama.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert len(data["data"]) == 2
    assert data["data"][0]["episode_number"] == 1


@pytest.mark.asyncio
async def test_create_episode(client: AsyncClient, db_session: AsyncSession):
    """测试创建集数"""
    from src.dramas.service import DramaService

    service = DramaService(db_session)
    drama = await service.create({
        "title": "测试剧集目",
        "genre": "科幻",
    })

    response = await client.post(
        f"/api/v1/dramas/episodes/create?drama_id={drama.id}",
        params={
            "episode_number": 1,
            "title": "第一集",
            "description": "开篇",
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["episode_number"] == 1
    assert data["data"]["title"] == "第一集"


@pytest.mark.asyncio
async def test_list_characters(client: AsyncClient, db_session: AsyncSession):
    """测试获取剧目角色列表"""
    from src.dramas.service import DramaService

    service = DramaService(db_session)

    # 创建剧目
    drama = await service.create({
        "title": "测试角色剧目",
        "genre": "科幻",
    })

    # 创建角色
    await service.create_character(drama.id, {
        "name": "主角",
        "role": "主角",
    })
    await service.create_character(drama.id, {
        "name": "配角",
        "role": "配角",
    })

    response = await client.get(f"/api/v1/dramas/characters/list?drama_id={drama.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert len(data["data"]) == 2
    assert data["data"][0]["name"] == "主角"


@pytest.mark.asyncio
async def test_get_drama_stats(client: AsyncClient):
    """测试获取剧目统计"""
    response = await client.get("/api/v1/dramas/stats")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "total_dramas" in data["data"]
    assert "total_episodes" in data["data"]
    assert "total_characters" in data["data"]


@pytest.mark.asyncio
async def test_batch_save_characters(client: AsyncClient, db_session: AsyncSession):
    """测试批量保存角色"""
    from src.dramas.service import DramaService

    service = DramaService(db_session)
    drama = await service.create({
        "title": "批量角色测试",
        "genre": "科幻",
    })

    response = await client.post(
        f"/api/v1/dramas/characters/batch-save?drama_id={drama.id}",
        json={
            "characters": [
                {"name": "角色1", "role": "主角"},
                {"name": "角色2", "role": "配角"},
            ]
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["count"] == 2


@pytest.mark.asyncio
async def test_save_outline(client: AsyncClient, db_session: AsyncSession):
    """测试保存大纲"""
    from src.dramas.service import DramaService

    service = DramaService(db_session)
    drama = await service.create({
        "title": "大纲测试",
        "genre": "科幻",
    })

    outline_data = {
        "outline": {
            "acts": ["第一幕", "第二幕"],
            "themes": ["爱情", "冒险"],
        }
    }

    response = await client.post(
        f"/api/v1/dramas/outline/save?drama_id={drama.id}",
        json=outline_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "成功" in data["message"]


@pytest.mark.asyncio
async def test_save_progress(client: AsyncClient, db_session: AsyncSession):
    """测试保存进度"""
    from src.dramas.service import DramaService

    service = DramaService(db_session)
    drama = await service.create({
        "title": "进度测试",
        "genre": "科幻",
    })

    progress_data = {
        "progress": {
            "completed_episodes": 5,
            "total_scenes": 100,
        },
        "status": "producing",
    }

    response = await client.post(
        f"/api/v1/dramas/progress/save?drama_id={drama.id}",
        json=progress_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["status"] == "producing"
