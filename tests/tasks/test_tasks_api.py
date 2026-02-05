"""
任务 API 测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_list_tasks_empty(client: AsyncClient):
    """测试获取空任务列表"""
    response = await client.get("/api/v1/tasks/list")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["total"] == 0
    assert data["data"]["items"] == []


@pytest.mark.asyncio
async def test_get_task_status_not_found(client: AsyncClient):
    """测试获取不存在的任务状态"""
    response = await client.get("/api/v1/tasks/status?task_id=nonexistent-id")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] != 200
    assert "不存在" in data["message"]


@pytest.mark.asyncio
async def test_cancel_task_not_found(client: AsyncClient):
    """测试取消不存在的任务"""
    response = await client.post("/api/v1/tasks/cancel?task_id=nonexistent-id")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["canceled"] is False


@pytest.mark.asyncio
async def test_list_tasks_by_resource(client: AsyncClient, db_session: AsyncSession):
    """测试按资源筛选任务列表"""
    from app.models.task import AsyncTask
    from src.tasks.service import TaskService
    import uuid

    service = TaskService(db_session)

    # 创建测试任务
    task1 = AsyncTask(
        id=str(uuid.uuid4()),
        type="test_task",
        status="pending",
        resource_id="resource123"
    )
    task2 = AsyncTask(
        id=str(uuid.uuid4()),
        type="test_task",
        status="completed",
        resource_id="resource123"
    )
    task3 = AsyncTask(
        id=str(uuid.uuid4()),
        type="test_task",
        status="pending",
        resource_id="other_resource"
    )

    db_session.add_all([task1, task2, task3])
    await db_session.commit()

    # 测试按资源筛选
    response = await client.get("/api/v1/tasks/list?resource_id=resource123")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["total"] == 2
    assert len(data["data"]["items"]) == 2


@pytest.mark.asyncio
async def test_list_tasks_by_type(client: AsyncClient, db_session: AsyncSession):
    """测试按类型筛选任务列表"""
    from app.models.task import AsyncTask
    import uuid

    # 创建测试任务
    task1 = AsyncTask(
        id=str(uuid.uuid4()),
        type="image_generation",
        status="pending",
        resource_id="resource1"
    )
    task2 = AsyncTask(
        id=str(uuid.uuid4()),
        type="video_generation",
        status="pending",
        resource_id="resource2"
    )
    task3 = AsyncTask(
        id=str(uuid.uuid4()),
        type="image_generation",
        status="completed",
        resource_id="resource3"
    )

    db_session.add_all([task1, task2, task3])
    await db_session.commit()

    # 测试按类型筛选
    response = await client.get("/api/v1/tasks/list?task_type=image_generation")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["total"] == 2
    assert all(item["type"] == "image_generation" for item in data["data"]["items"])


@pytest.mark.asyncio
async def test_list_tasks_pagination(client: AsyncClient, db_session: AsyncSession):
    """测试任务列表分页"""
    from app.models.task import AsyncTask
    import uuid

    # 创建多个测试任务
    tasks = []
    for i in range(5):
        task = AsyncTask(
            id=str(uuid.uuid4()),
            type="test_task",
            status="pending",
            resource_id=f"resource{i}"
        )
        tasks.append(task)

    db_session.add_all(tasks)
    await db_session.commit()

    # 测试第一页
    response = await client.get("/api/v1/tasks/list?page=1&page_size=2")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["total"] >= 5
    assert len(data["data"]["items"]) == 2


@pytest.mark.asyncio
async def test_get_resource_tasks(client: AsyncClient, db_session: AsyncSession):
    """测试获取资源的所有任务"""
    from app.models.task import AsyncTask
    import uuid

    # 创建测试任务
    task1 = AsyncTask(
        id=str(uuid.uuid4()),
        type="image_generation",
        status="pending",
        resource_id="resource123"
    )
    task2 = AsyncTask(
        id=str(uuid.uuid4()),
        type="video_generation",
        status="processing",
        resource_id="resource123"
    )
    task3 = AsyncTask(
        id=str(uuid.uuid4()),
        type="image_generation",
        status="completed",
        resource_id="other_resource"
    )

    db_session.add_all([task1, task2, task3])
    await db_session.commit()

    # 测试获取资源任务
    response = await client.get("/api/v1/tasks/by-resource?resource_id=resource123")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert len(data["data"]) == 2
    assert all(task["resource_id"] == "resource123" for task in data["data"])


@pytest.mark.asyncio
async def test_get_resource_tasks_with_type_filter(client: AsyncClient, db_session: AsyncSession):
    """测试获取资源任务并按类型筛选"""
    from app.models.task import AsyncTask
    import uuid

    # 创建测试任务
    task1 = AsyncTask(
        id=str(uuid.uuid4()),
        type="image_generation",
        status="pending",
        resource_id="resource123"
    )
    task2 = AsyncTask(
        id=str(uuid.uuid4()),
        type="video_generation",
        status="processing",
        resource_id="resource123"
    )

    db_session.add_all([task1, task2])
    await db_session.commit()

    # 测试获取资源任务并筛选类型
    response = await client.get("/api/v1/tasks/by-resource?resource_id=resource123&task_type=image_generation")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert len(data["data"]) == 1
    assert data["data"][0]["type"] == "image_generation"


@pytest.mark.asyncio
async def test_task_status_progress_values(client: AsyncClient, db_session: AsyncSession):
    """测试任务状态中的进度值范围"""
    from app.models.task import AsyncTask
    from src.tasks.service import TaskService
    import uuid

    service = TaskService(db_session)

    # 创建不同状态的任务
    task_pending = AsyncTask(
        id=str(uuid.uuid4()),
        type="test_task",
        status="pending",
        progress=0,
        resource_id="resource1"
    )
    task_processing = AsyncTask(
        id=str(uuid.uuid4()),
        type="test_task",
        status="processing",
        progress=50,
        resource_id="resource2"
    )
    task_completed = AsyncTask(
        id=str(uuid.uuid4()),
        type="test_task",
        status="completed",
        progress=100,
        resource_id="resource3"
    )

    db_session.add_all([task_pending, task_processing, task_completed])
    await db_session.commit()

    # 获取处理中的任务
    response = await client.get(f"/api/v1/tasks/status?task_id={task_processing.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["status"] == "processing"
    assert data["data"]["progress"] == 50
