"""
资源 API 测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_list_assets_empty(client: AsyncClient):
    """测试获取空的资源列表"""
    response = await client.get("/api/v1/assets/list")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["total"] == 0
    assert data["data"]["items"] == []


@pytest.mark.asyncio
async def test_create_asset(client: AsyncClient):
    """测试创建资源"""
    request_data = {
        "name": "测试图片",
        "type": "image",
        "url": "https://example.com/test.jpg",
        "description": "这是一个测试图片",
        "category": "场景图",
        "width": 1920,
        "height": 1080,
    }

    response = await client.post("/api/v1/assets/create", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["name"] == "测试图片"
    assert data["data"]["type"] == "image"


@pytest.mark.asyncio
async def test_create_asset_validation_error(client: AsyncClient):
    """测试创建资源 - 验证错误"""
    # 缺少必填字段
    request_data = {
        "name": "测试资源",
        # 缺少 type 和 url
    }

    response = await client.post("/api/v1/assets/create", json=request_data)

    assert response.status_code == 422  # Pydantic 验证错误


@pytest.mark.asyncio
async def test_get_asset(client: AsyncClient, db_session: AsyncSession):
    """测试获取资源详情"""
    from app.models.asset import Asset
    from src.assets.service import AssetService

    service = AssetService(db_session)
    asset = await service.create({
        "name": "详情测试资源",
        "type": "video",
        "url": "https://example.com/test.mp4",
    })

    response = await client.get(f"/api/v1/assets/info?asset_id={asset.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["id"] == asset.id
    assert data["data"]["name"] == "详情测试资源"
    # 浏览次数应该增加
    assert data["data"]["view_count"] >= 1


@pytest.mark.asyncio
async def test_get_asset_not_found(client: AsyncClient):
    """测试获取不存在的资源"""
    response = await client.get("/api/v1/assets/info?asset_id=99999")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] != 200  # 应该返回错误码
    assert "不存在" in data["message"]


@pytest.mark.asyncio
async def test_update_asset(client: AsyncClient, db_session: AsyncSession):
    """测试更新资源"""
    from src.assets.service import AssetService

    service = AssetService(db_session)
    asset = await service.create({
        "name": "更新前",
        "type": "image",
        "url": "https://example.com/before.jpg",
    })

    update_data = {
        "name": "更新后",
        "description": "已更新描述",
    }

    response = await client.post(
        f"/api/v1/assets/update?asset_id={asset.id}",
        json=update_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["name"] == "更新后"
    assert data["data"]["description"] == "已更新描述"


@pytest.mark.asyncio
async def test_delete_asset(client: AsyncClient, db_session: AsyncSession):
    """测试删除资源"""
    from src.assets.service import AssetService

    service = AssetService(db_session)
    asset = await service.create({
        "name": "待删除",
        "type": "audio",
        "url": "https://example.com/delete.mp3",
    })

    response = await client.post(f"/api/v1/assets/delete?asset_id={asset.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["asset_id"] == asset.id

    # 验证删除后无法找到
    get_response = await client.get(f"/api/v1/assets/info?asset_id={asset.id}")
    assert get_response.json()["code"] != 200


@pytest.mark.asyncio
async def test_list_assets_with_filters(client: AsyncClient, db_session: AsyncSession):
    """测试带过滤条件的资源列表"""
    from src.assets.service import AssetService

    service = AssetService(db_session)

    # 创建多个资源
    await service.create({
        "name": "图片1",
        "type": "image",
        "url": "https://example.com/img1.jpg",
        "category": "场景",
    })
    await service.create({
        "name": "视频1",
        "type": "video",
        "url": "https://example.com/video1.mp4",
        "category": "分镜",
    })
    await service.create({
        "name": "图片2",
        "type": "image",
        "url": "https://example.com/img2.jpg",
        "category": "场景",
    })

    # 测试类型过滤
    response = await client.get("/api/v1/assets/list?type=image")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["total"] >= 2

    # 测试分类过滤
    response = await client.get("/api/v1/assets/list?category=分镜")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["total"] >= 1


@pytest.mark.asyncio
async def test_import_from_image_gen_not_found(client: AsyncClient):
    """测试从不存在的图片生成记录导入"""
    response = await client.post(
        "/api/v1/assets/import/image?image_gen_id=99999&name=测试资源"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] != 200  # 应该返回错误
    assert "不存在" in data["message"]


@pytest.mark.asyncio
async def test_import_from_video_gen_not_found(client: AsyncClient):
    """测试从不存在的视频生成记录导入"""
    response = await client.post(
        "/api/v1/assets/import/video?video_gen_id=99999&name=测试资源"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["code"] != 200  # 应该返回错误
    assert "不存在" in data["message"]
