"""
场景 API 测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_list_scenes_empty(client: AsyncClient):
    """测试获取空场景列表"""
    response = await client.get("/api/v1/scenes/list")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["total"] == 0
    assert data["data"]["items"] == []


@pytest.mark.asyncio
async def test_list_scenes_by_drama(client: AsyncClient, db_session: AsyncSession):
    """测试获取指定剧目的场景列表"""
    from src.dramas.service import DramaService
    from src.scenes.service import SceneService

    drama_service = DramaService(db_session)
    scene_service = SceneService(db_session)

    # 创建剧目
    drama = await drama_service.create({
        "title": "测试剧目",
        "genre": "科幻",
    })

    # 创建场景
    await scene_service.create(drama.id, {
        "location": "实验室",
        "time": "白天",
        "prompt": "科幻实验室场景",
    })
    await scene_service.create(drama.id, {
        "location": "太空舱",
        "time": "夜晚",
        "prompt": "太空舱内部",
    })

    response = await client.get(f"/api/v1/scenes/list?drama_id={drama.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["total"] == 2
    assert len(data["data"]["items"]) == 2


@pytest.mark.asyncio
async def test_get_scene_info(client: AsyncClient, db_session: AsyncSession):
    """测试获取场景详情"""
    from src.dramas.service import DramaService
    from src.scenes.service import SceneService

    drama_service = DramaService(db_session)
    scene_service = SceneService(db_session)

    # 创建剧目和场景
    drama = await drama_service.create({
        "title": "测试剧目",
        "genre": "科幻",
    })
    scene = await scene_service.create(drama.id, {
        "location": "实验室",
        "time": "白天",
        "prompt": "科幻实验室",
    })

    response = await client.get(f"/api/v1/scenes/info?scene_id={scene.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["id"] == scene.id
    assert data["data"]["location"] == "实验室"
    assert data["data"]["drama_id"] == drama.id


@pytest.mark.asyncio
async def test_get_scene_not_found(client: AsyncClient):
    """测试获取不存在的场景"""
    response = await client.get("/api/v1/scenes/info?scene_id=99999")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] != 200
    assert "不存在" in data["message"]


@pytest.mark.asyncio
async def test_update_scene(client: AsyncClient, db_session: AsyncSession):
    """测试更新场景"""
    from src.dramas.service import DramaService
    from src.scenes.service import SceneService

    drama_service = DramaService(db_session)
    scene_service = SceneService(db_session)

    # 创建剧目和场景
    drama = await drama_service.create({
        "title": "测试剧目",
        "genre": "科幻",
    })
    scene = await scene_service.create(drama.id, {
        "location": "实验室",
        "time": "白天",
        "prompt": "旧提示词",
    })

    update_data = {
        "location": "控制中心",
        "prompt": "新提示词",
    }

    response = await client.post(
        f"/api/v1/scenes/update?scene_id={scene.id}",
        json=update_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["location"] == "控制中心"
    assert data["data"]["prompt"] == "新提示词"


@pytest.mark.asyncio
async def test_update_scene_prompt(client: AsyncClient, db_session: AsyncSession):
    """测试更新场景提示词"""
    from src.dramas.service import DramaService
    from src.scenes.service import SceneService

    drama_service = DramaService(db_session)
    scene_service = SceneService(db_session)

    # 创建剧目和场景
    drama = await drama_service.create({
        "title": "测试剧目",
        "genre": "科幻",
    })
    scene = await scene_service.create(drama.id, {
        "location": "实验室",
        "time": "白天",
        "prompt": "旧提示词",
    })

    response = await client.post(
        f"/api/v1/scenes/update-prompt?scene_id={scene.id}",
        json={"prompt": "新的 AI 提示词"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["prompt"] == "新的 AI 提示词"


@pytest.mark.asyncio
async def test_delete_scene(client: AsyncClient, db_session: AsyncSession):
    """测试删除场景"""
    from src.dramas.service import DramaService
    from src.scenes.service import SceneService

    drama_service = DramaService(db_session)
    scene_service = SceneService(db_session)

    # 创建剧目和场景
    drama = await drama_service.create({
        "title": "测试剧目",
        "genre": "科幻",
    })
    scene = await scene_service.create(drama.id, {
        "location": "实验室",
        "time": "白天",
        "prompt": "待删除",
    })

    response = await client.post(f"/api/v1/scenes/delete?scene_id={scene.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["scene_id"] == scene.id

    # 验证删除后无法找到
    get_response = await client.get(f"/api/v1/scenes/info?scene_id={scene.id}")
    assert get_response.json()["code"] != 200


@pytest.mark.asyncio
async def test_generate_scene_image(client: AsyncClient, db_session: AsyncSession):
    """测试生成场景图片"""
    from src.dramas.service import DramaService
    from src.scenes.service import SceneService

    drama_service = DramaService(db_session)
    scene_service = SceneService(db_session)

    # 创建剧目和场景
    drama = await drama_service.create({
        "title": "测试剧目",
        "genre": "科幻",
    })
    scene = await scene_service.create(drama.id, {
        "location": "实验室",
        "time": "白天",
        "prompt": "科幻实验室场景",
    })

    response = await client.post(f"/api/v1/scenes/generate-image?scene_id={scene.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "task_id" in data["data"]
    assert data["data"]["status"] == "pending"


@pytest.mark.asyncio
async def test_list_scenes_by_episode(client: AsyncClient, db_session: AsyncSession):
    """测试通过集数获取场景列表"""
    from src.dramas.service import DramaService
    from src.scenes.service import SceneService

    drama_service = DramaService(db_session)
    scene_service = SceneService(db_session)

    # 创建剧目和集数
    drama = await drama_service.create({
        "title": "测试剧目",
        "genre": "科幻",
    })
    episode = await drama_service.create_episode(drama.id, {
        "episode_number": 1,
        "title": "第一集",
    })

    # 创建场景
    await scene_service.create(drama.id, {
        "episode_id": episode.id,
        "location": "实验室",
        "time": "白天",
        "prompt": "场景1",
    })
    await scene_service.create(drama.id, {
        "episode_id": episode.id,
        "location": "走廊",
        "time": "夜晚",
        "prompt": "场景2",
    })

    response = await client.get(f"/api/v1/scenes/list?episode_id={episode.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["total"] == 2
    assert len(data["data"]["items"]) == 2


@pytest.mark.asyncio
async def test_list_scenes_by_drama_endpoint(client: AsyncClient, db_session: AsyncSession):
    """测试通过剧目获取场景列表的端点"""
    from src.dramas.service import DramaService
    from src.scenes.service import SceneService

    drama_service = DramaService(db_session)
    scene_service = SceneService(db_session)

    # 创建剧目
    drama = await drama_service.create({
        "title": "测试剧目",
        "genre": "科幻",
    })

    # 创建场景
    await scene_service.create(drama.id, {
        "location": "实验室",
        "time": "白天",
        "prompt": "场景1",
    })
    await scene_service.create(drama.id, {
        "location": "走廊",
        "time": "夜晚",
        "prompt": "场景2",
    })

    response = await client.get(f"/api/v1/scenes/by-drama?drama_id={drama.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert len(data["data"]) == 2


@pytest.mark.asyncio
async def test_list_scenes_pagination(client: AsyncClient, db_session: AsyncSession):
    """测试场景列表分页"""
    from src.dramas.service import DramaService
    from src.scenes.service import SceneService

    drama_service = DramaService(db_session)
    scene_service = SceneService(db_session)

    # 创建剧目
    drama = await drama_service.create({
        "title": "多场景测试",
        "genre": "科幻",
    })

    # 创建多个场景
    for i in range(5):
        await scene_service.create(drama.id, {
            "location": f"地点{i}",
            "time": "白天",
            "prompt": f"场景{i}",
        })

    # 测试第一页
    response = await client.get(
        f"/api/v1/scenes/list?drama_id={drama.id}&page=1&page_size=2"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["total"] == 5
    assert len(data["data"]["items"]) == 2

    # 测试第二页
    response = await client.get(
        f"/api/v1/scenes/list?drama_id={drama.id}&page=2&page_size=2"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert len(data["data"]["items"]) == 2
