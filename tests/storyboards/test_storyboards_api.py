"""
分镜 API 测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_list_storyboards_empty(client: AsyncClient):
    """测试获取空分镜列表"""
    response = await client.get("/api/v1/storyboards/list")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["total"] == 0
    assert data["data"]["items"] == []


@pytest.mark.asyncio
async def test_list_storyboards_by_episode(client: AsyncClient, db_session: AsyncSession):
    """测试获取指定集数的分镜列表"""
    from src.dramas.service import DramaService
    from app.models.drama import Storyboard

    drama_service = DramaService(db_session)

    # 创建剧目和集数
    drama = await drama_service.create({
        "title": "测试剧目",
        "genre": "科幻",
    })
    episode = await drama_service.create_episode(drama.id, {
        "episode_number": 1,
        "title": "第一集",
    })

    # 创建分镜
    storyboard1 = Storyboard(
        drama_id=drama.id,
        episode_id=episode.id,
        storyboard_number=1,
        title="分镜1",
        status="pending"
    )
    storyboard2 = Storyboard(
        drama_id=drama.id,
        episode_id=episode.id,
        storyboard_number=2,
        title="分镜2",
        status="pending"
    )

    db_session.add_all([storyboard1, storyboard2])
    await db_session.commit()

    response = await client.get(f"/api/v1/storyboards/list?episode_id={episode.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["total"] == 2
    assert len(data["data"]["items"]) == 2


@pytest.mark.asyncio
async def test_get_storyboard_info(client: AsyncClient, db_session: AsyncSession):
    """测试获取分镜详情"""
    from src.dramas.service import DramaService
    from app.models.drama import Storyboard

    drama_service = DramaService(db_session)

    # 创建剧目和集数
    drama = await drama_service.create({
        "title": "测试剧目",
        "genre": "科幻",
    })
    episode = await drama_service.create_episode(drama.id, {
        "episode_number": 1,
        "title": "第一集",
    })

    # 创建分镜
    storyboard = Storyboard(
        drama_id=drama.id,
        episode_id=episode.id,
        storyboard_number=1,
        title="测试分镜",
        shot_type="wide",
        status="pending"
    )
    db_session.add(storyboard)
    await db_session.commit()
    await db_session.refresh(storyboard)

    response = await client.get(f"/api/v1/storyboards/info?storyboard_id={storyboard.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["id"] == storyboard.id
    assert data["data"]["title"] == "测试分镜"
    assert data["data"]["shot_type"] == "wide"


@pytest.mark.asyncio
async def test_get_storyboard_not_found(client: AsyncClient):
    """测试获取不存在的分镜"""
    response = await client.get("/api/v1/storyboards/info?storyboard_id=99999")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] != 200
    assert "不存在" in data["message"]


@pytest.mark.asyncio
async def test_update_storyboard(client: AsyncClient, db_session: AsyncSession):
    """测试更新分镜"""
    from src.dramas.service import DramaService
    from app.models.drama import Storyboard

    drama_service = DramaService(db_session)

    # 创建剧目和集数
    drama = await drama_service.create({
        "title": "测试剧目",
        "genre": "科幻",
    })
    episode = await drama_service.create_episode(drama.id, {
        "episode_number": 1,
        "title": "第一集",
    })

    # 创建分镜
    storyboard = Storyboard(
        drama_id=drama.id,
        episode_id=episode.id,
        storyboard_number=1,
        title="更新前",
        shot_type="wide",
        status="pending"
    )
    db_session.add(storyboard)
    await db_session.commit()
    await db_session.refresh(storyboard)

    update_data = {
        "title": "更新后",
        "shot_type": "close-up",
        "description": "特写镜头",
    }

    response = await client.post(
        f"/api/v1/storyboards/update?storyboard_id={storyboard.id}",
        json=update_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["title"] == "更新后"
    assert data["data"]["shot_type"] == "close-up"
    assert data["data"]["description"] == "特写镜头"


@pytest.mark.asyncio
async def test_delete_storyboard(client: AsyncClient, db_session: AsyncSession):
    """测试删除分镜"""
    from src.dramas.service import DramaService
    from app.models.drama import Storyboard

    drama_service = DramaService(db_session)

    # 创建剧目和集数
    drama = await drama_service.create({
        "title": "测试剧目",
        "genre": "科幻",
    })
    episode = await drama_service.create_episode(drama.id, {
        "episode_number": 1,
        "title": "第一集",
    })

    # 创建分镜
    storyboard = Storyboard(
        drama_id=drama.id,
        episode_id=episode.id,
        storyboard_number=1,
        title="待删除",
        status="pending"
    )
    db_session.add(storyboard)
    await db_session.commit()
    await db_session.refresh(storyboard)

    response = await client.post(f"/api/v1/storyboards/delete?storyboard_id={storyboard.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["storyboard_id"] == storyboard.id


@pytest.mark.asyncio
async def test_list_storyboards_by_episode_endpoint(client: AsyncClient, db_session: AsyncSession):
    """测试通过集数获取分镜列表的端点"""
    from src.dramas.service import DramaService
    from app.models.drama import Storyboard

    drama_service = DramaService(db_session)

    # 创建剧目和集数
    drama = await drama_service.create({
        "title": "测试剧目",
        "genre": "科幻",
    })
    episode = await drama_service.create_episode(drama.id, {
        "episode_number": 1,
        "title": "第一集",
    })

    # 创建分镜
    storyboard1 = Storyboard(
        drama_id=drama.id,
        episode_id=episode.id,
        storyboard_number=1,
        title="分镜1",
        status="pending"
    )
    storyboard2 = Storyboard(
        drama_id=drama.id,
        episode_id=episode.id,
        storyboard_number=2,
        title="分镜2",
        status="pending"
    )

    db_session.add_all([storyboard1, storyboard2])
    await db_session.commit()

    response = await client.get(f"/api/v1/storyboards/by-episode?episode_id={episode.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert len(data["data"]) == 2
    assert data["data"][0]["storyboard_number"] == 1


@pytest.mark.asyncio
async def test_generate_frame_prompt(client: AsyncClient, db_session: AsyncSession):
    """测试生成帧提示词"""
    from src.dramas.service import DramaService
    from app.models.drama import Storyboard

    drama_service = DramaService(db_session)

    # 创建剧目和集数
    drama = await drama_service.create({
        "title": "测试剧目",
        "genre": "科幻",
    })
    episode = await drama_service.create_episode(drama.id, {
        "episode_number": 1,
        "title": "第一集",
    })

    # 创建分镜
    storyboard = Storyboard(
        drama_id=drama.id,
        episode_id=episode.id,
        storyboard_number=1,
        title="测试分镜",
        image_prompt="一个科幻实验室的广角镜头",
        status="pending"
    )
    db_session.add(storyboard)
    await db_session.commit()
    await db_session.refresh(storyboard)

    response = await client.post(
        f"/api/v1/storyboards/frame-prompt?storyboard_id={storyboard.id}&frame_type=key"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["storyboard_id"] == storyboard.id
    assert data["data"]["frame_type"] == "key"


@pytest.mark.asyncio
async def test_get_storyboard_frame_prompts(client: AsyncClient, db_session: AsyncSession):
    """测试获取分镜的帧提示词"""
    from src.dramas.service import DramaService
    from app.models.frame_prompt import FramePrompt

    drama_service = DramaService(db_session)

    # 创建剧目和集数
    drama = await drama_service.create({
        "title": "测试剧目",
        "genre": "科幻",
    })
    episode = await drama_service.create_episode(drama.id, {
        "episode_number": 1,
        "title": "第一集",
    })

    # 创建分镜
    storyboard = Storyboard(
        drama_id=drama.id,
        episode_id=episode.id,
        storyboard_number=1,
        title="测试分镜",
        status="pending"
    )
    db_session.add(storyboard)
    await db_session.commit()
    await db_session.refresh(storyboard)

    # 创建帧提示词
    frame_prompt1 = FramePrompt(
        storyboard_id=storyboard.id,
        frame_type="first",
        prompt="第一帧提示词"
    )
    frame_prompt2 = FramePrompt(
        storyboard_id=storyboard.id,
        frame_type="key",
        prompt="关键帧提示词"
    )

    db_session.add_all([frame_prompt1, frame_prompt2])
    await db_session.commit()

    response = await client.get(f"/api/v1/storyboards/frame-prompts?storyboard_id={storyboard.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["storyboard_id"] == storyboard.id
    assert data["data"]["count"] == 2
    assert len(data["data"]["frame_prompts"]) == 2


@pytest.mark.asyncio
async def test_generate_storyboards(client: AsyncClient, db_session: AsyncSession):
    """测试生成分镜"""
    from src.dramas.service import DramaService

    drama_service = DramaService(db_session)

    # 创建剧目和集数
    drama = await drama_service.create({
        "title": "测试剧目",
        "genre": "科幻",
    })
    episode = await drama_service.create_episode(drama.id, {
        "episode_number": 1,
        "title": "第一集",
    })

    response = await client.post(
        f"/api/v1/storyboards/generate?episode_id={episode.id}",
        json={"num_shots_per_scene": 3}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "task_id" in data["data"]
    assert data["data"]["status"] == "pending"
