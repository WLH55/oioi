"""
集数 API 测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_list_episodes_empty(client: AsyncClient):
    """测试获取空的集数列表"""
    response = await client.get("/api/v1/episodes/list")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["total"] == 0
    assert data["data"]["items"] == []


@pytest.mark.asyncio
async def test_list_episodes_by_drama(client: AsyncClient, db_session: AsyncSession):
    """测试获取指定剧目的集数列表"""
    from src.dramas.service import DramaService

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

    response = await client.get(f"/api/v1/episodes/list?drama_id={drama.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["total"] == 2
    assert len(data["data"]["items"]) == 2


@pytest.mark.asyncio
async def test_get_episode_info(client: AsyncClient, db_session: AsyncSession):
    """测试获取集数详情"""
    from src.dramas.service import DramaService

    service = DramaService(db_session)

    # 创建剧目和集数
    drama = await service.create({
        "title": "测试剧集目",
        "genre": "科幻",
    })
    episode = await service.create_episode(drama.id, {
        "episode_number": 1,
        "title": "第一集",
        "description": "开篇",
    })

    response = await client.get(f"/api/v1/episodes/info?episode_id={episode.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["id"] == episode.id
    assert data["data"]["title"] == "第一集"
    assert data["data"]["drama_id"] == drama.id


@pytest.mark.asyncio
async def test_get_episode_not_found(client: AsyncClient):
    """测试获取不存在的集数"""
    response = await client.get("/api/v1/episodes/info?episode_id=99999")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] != 200
    assert "不存在" in data["message"]


@pytest.mark.asyncio
async def test_update_episode(client: AsyncClient, db_session: AsyncSession):
    """测试更新集数"""
    from src.dramas.service import DramaService

    service = DramaService(db_session)

    # 创建剧目和集数
    drama = await service.create({
        "title": "测试剧集目",
        "genre": "科幻",
    })
    episode = await service.create_episode(drama.id, {
        "episode_number": 1,
        "title": "更新前",
    })

    update_data = {
        "title": "更新后",
        "description": "已更新描述",
        "duration": 300,
    }

    response = await client.post(
        f"/api/v1/episodes/update?episode_id={episode.id}",
        json=update_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["title"] == "更新后"
    assert data["data"]["description"] == "已更新描述"
    assert data["data"]["duration"] == 300


@pytest.mark.asyncio
async def test_delete_episode(client: AsyncClient, db_session: AsyncSession):
    """测试删除集数"""
    from src.dramas.service import DramaService

    service = DramaService(db_session)

    # 创建剧目和集数
    drama = await service.create({
        "title": "测试剧集目",
        "genre": "科幻",
    })
    episode = await service.create_episode(drama.id, {
        "episode_number": 1,
        "title": "待删除",
    })

    response = await client.post(f"/api/v1/episodes/delete?episode_id={episode.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["episode_id"] == episode.id

    # 验证删除后无法找到
    get_response = await client.get(f"/api/v1/episodes/info?episode_id={episode.id}")
    assert get_response.json()["code"] != 200


@pytest.mark.asyncio
async def test_finalize_episode(client: AsyncClient, db_session: AsyncSession):
    """测试完成集数制作"""
    from src.dramas.service import DramaService

    service = DramaService(db_session)

    # 创建剧目和集数
    drama = await service.create({
        "title": "测试剧集目",
        "genre": "科幻",
    })
    episode = await service.create_episode(drama.id, {
        "episode_number": 1,
        "title": "待完成",
    })

    response = await client.post(f"/api/v1/episodes/finalize?episode_id={episode.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "task_id" in data["data"]
    assert data["data"]["status"] == "processing"


@pytest.mark.asyncio
async def test_get_episode_download_no_video(client: AsyncClient, db_session: AsyncSession):
    """测试获取没有视频的集数下载信息"""
    from src.dramas.service import DramaService

    service = DramaService(db_session)

    # 创建剧目和集数（没有视频）
    drama = await service.create({
        "title": "测试剧集目",
        "genre": "科幻",
    })
    episode = await service.create_episode(drama.id, {
        "episode_number": 1,
        "title": "无视频",
    })

    response = await client.get(f"/api/v1/episodes/download?episode_id={episode.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] != 200
    assert "视频" in data["message"]


@pytest.mark.asyncio
async def test_get_episode_download_with_video(client: AsyncClient, db_session: AsyncSession):
    """测试获取有视频的集数下载信息"""
    from src.dramas.service import DramaService
    from app.models.drama import Episode

    service = DramaService(db_session)

    # 创建剧目和集数
    drama = await service.create({
        "title": "测试剧集目",
        "genre": "科幻",
    })
    episode = await service.create_episode(drama.id, {
        "episode_number": 1,
        "title": "有视频",
    })

    # 手动设置视频URL
    episode.video_url = "http://example.com/video.mp4"
    episode.duration = 600
    await db_session.commit()

    response = await client.get(f"/api/v1/episodes/download?episode_id={episode.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["video_url"] == "http://example.com/video.mp4"
    assert data["data"]["duration"] == 600


@pytest.mark.asyncio
async def test_list_episodes_by_drama_endpoint(client: AsyncClient, db_session: AsyncSession):
    """测试通过剧目获取集数列表的端点"""
    from src.dramas.service import DramaService

    service = DramaService(db_session)

    # 创建剧目和集数
    drama = await service.create({
        "title": "测试剧集目",
        "genre": "科幻",
    })
    await service.create_episode(drama.id, {
        "episode_number": 1,
        "title": "第一集",
    })
    await service.create_episode(drama.id, {
        "episode_number": 2,
        "title": "第二集",
    })

    response = await client.get(f"/api/v1/episodes/by-drama?drama_id={drama.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert len(data["data"]) == 2
    assert data["data"][0]["episode_number"] == 1


@pytest.mark.asyncio
async def test_list_episodes_pagination(client: AsyncClient, db_session: AsyncSession):
    """测试集数列表分页"""
    from src.dramas.service import DramaService

    service = DramaService(db_session)

    # 创建剧目和多集
    drama = await service.create({
        "title": "多集测试",
        "genre": "科幻",
    })

    for i in range(5):
        await service.create_episode(drama.id, {
            "episode_number": i + 1,
            "title": f"第{i+1}集",
        })

    # 测试第一页
    response = await client.get(
        f"/api/v1/episodes/list?drama_id={drama.id}&page=1&page_size=2"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["total"] == 5
    assert len(data["data"]["items"]) == 2

    # 测试第二页
    response = await client.get(
        f"/api/v1/episodes/list?drama_id={drama.id}&page=2&page_size=2"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert len(data["data"]["items"]) == 2
