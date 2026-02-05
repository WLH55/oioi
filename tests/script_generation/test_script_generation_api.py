"""
剧本生成 API 测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_generate_characters(client: AsyncClient, db_session: AsyncSession):
    """测试生成角色"""
    from src.dramas.service import DramaService

    service = DramaService(db_session)

    # 创建剧目
    drama = await service.create({
        "title": "测试剧目",
        "genre": "科幻",
        "style": "realistic",
    })

    request_data = {
        "drama_id": drama.id,
        "genre": "科幻",
        "style": "realistic",
        "num_characters": 2,
    }

    response = await client.post(
        "/api/v1/generation/characters",
        json=request_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["drama_id"] == drama.id
    assert data["data"]["count"] == 2
    assert len(data["data"]["characters"]) == 2


@pytest.mark.asyncio
async def test_generate_characters_with_custom_prompt(client: AsyncClient, db_session: AsyncSession):
    """测试使用自定义提示词生成角色"""
    from src.dramas.service import DramaService

    service = DramaService(db_session)

    # 创建剧目
    drama = await service.create({
        "title": "测试剧目",
        "genre": "科幻",
    })

    request_data = {
        "drama_id": drama.id,
        "num_characters": 1,
        "custom_prompt": "生成一个勇敢的太空探险家角色",
    }

    response = await client.post(
        "/api/v1/generation/characters",
        json=request_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["count"] == 1
    assert "task_id" in data["data"]


@pytest.mark.asyncio
async def test_generate_script(client: AsyncClient, db_session: AsyncSession):
    """测试生成剧本"""
    from src.dramas.service import DramaService

    service = DramaService(db_session)

    # 创建剧目
    drama = await service.create({
        "title": "测试剧目",
        "genre": "科幻",
    })

    request_data = {
        "drama_id": drama.id,
        "episode_num": 1,
        "plot_outline": "主角在太空中发现了一个神秘信号",
        "duration": 20,
    }

    response = await client.post(
        "/api/v1/generation/script",
        json=request_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["drama_id"] == drama.id
    assert data["data"]["episode_num"] == 1
    assert data["data"]["title"] == "第1集"
    assert "script_length" in data["data"]


@pytest.mark.asyncio
async def test_generate_script_updates_existing_episode(client: AsyncClient, db_session: AsyncSession):
    """测试生成剧本会更新现有集数"""
    from src.dramas.service import DramaService

    service = DramaService(db_session)

    # 创建剧目和集数
    drama = await service.create({
        "title": "测试剧目",
        "genre": "科幻",
    })
    episode = await service.create_episode(drama.id, {
        "episode_number": 1,
        "title": "旧标题",
    })

    request_data = {
        "drama_id": drama.id,
        "episode_num": 1,
        "plot_outline": "新的剧情大纲",
    }

    response = await client.post(
        "/api/v1/generation/script",
        json=request_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["episode_id"] == episode.id


@pytest.mark.asyncio
async def test_generate_scenes_from_script(client: AsyncClient, db_session: AsyncSession):
    """测试从剧本生成场景"""
    from src.dramas.service import DramaService

    service = DramaService(db_session)

    # 创建剧目和集数
    drama = await service.create({
        "title": "测试剧目",
        "genre": "科幻",
    })
    episode = await service.create_episode(drama.id, {
        "episode_number": 1,
        "title": "第一集",
        "script_content": """
# 第一场：太空舱
[场景：太空舱内部，白天]

主角：大家好，我是探险队队长。

# 第二场：控制中心
[场景：控制中心，夜晚]

主角：发现了一个神秘信号！
        """.strip(),
    })

    response = await client.post(
        f"/api/v1/generation/scenes?episode_id={episode.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["episode_id"] == episode.id
    assert data["data"]["scenes_count"] > 0
    assert "scenes" in data["data"]
    assert "task_id" in data["data"]


@pytest.mark.asyncio
async def test_generate_scenes_no_script_content(client: AsyncClient, db_session: AsyncSession):
    """测试从没有剧本内容的集数生成场景"""
    from src.dramas.service import DramaService

    service = DramaService(db_session)

    # 创建剧目和集数（没有剧本内容）
    drama = await service.create({
        "title": "测试剧目",
        "genre": "科幻",
    })
    episode = await service.create_episode(drama.id, {
        "episode_number": 1,
        "title": "第一集",
    })

    response = await client.post(
        f"/api/v1/generation/scenes?episode_id={episode.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] != 200
    assert "剧本" in data["message"] or "内容" in data["message"]


@pytest.mark.asyncio
async def test_generate_characters_invalid_drama(client: AsyncClient):
    """测试为不存在的剧目生成角色"""
    request_data = {
        "drama_id": 99999,
        "num_characters": 2,
    }

    response = await client.post(
        "/api/v1/generation/characters",
        json=request_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] != 200
    assert "不存在" in data["message"]


@pytest.mark.asyncio
async def test_generate_script_invalid_drama(client: AsyncClient):
    """测试为不存在的剧目生成剧本"""
    request_data = {
        "drama_id": 99999,
        "episode_num": 1,
        "plot_outline": "测试大纲",
    }

    response = await client.post(
        "/api/v1/generation/script",
        json=request_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] != 200
    assert "不存在" in data["message"]
