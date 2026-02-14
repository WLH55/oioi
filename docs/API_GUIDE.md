# API 规范使用指南

## 概述

本项目使用统一的 API 响应格式和异常处理机制，确保所有 API 端点返回一致的数据结构。

## 核心组件

### 1. ApiResponse 统一响应格式

所有 API 端点返回 `ApiResponse` 格式：

```python
from src.schemas import ApiResponse

@router.get("/example")
async def example_endpoint() -> ApiResponse:
    return ApiResponse(data={"key": "value"})
```

**响应结构：**

```json
{
    "code": 200,
    "message": "success",
    "data": {...},
    "timestamp": 1234567890
}
```

### 2. ResponseCode 响应码

```python
from src.schemas import ResponseCode

# 常用响应码
ResponseCode.SUCCESS          # 200 - 成功
ResponseCode.BAD_REQUEST      # 400 - 请求参数错误
ResponseCode.UNAUTHORIZED     # 401 - 未授权
ResponseCode.FORBIDDEN        # 403 - 禁止访问
ResponseCode.NOT_FOUND        # 404 - 资源不存在
ResponseCode.INTERNAL_ERROR   # 500 - 服务器内部错误
```

### 3. 自定义异常

#### BusinessValidationException

用于业务逻辑验证失败：

```python
from src.exceptions import BusinessValidationException

async def create_drama(data: DramaCreate):
    if not data.title:
        raise BusinessValidationException("剧目标题不能为空")
```

#### HttpClientException

用于外部 API 调用失败：

```python
from src.exceptions import HttpClientException

async def call_ai_service(prompt: str):
    try:
        response = await ai_client.generate(prompt)
    except httpx.HTTPError as e:
        raise HttpClientException(
            message="AI 服务调用失败",
            code=503
        )
```

## 路由开发规范

### 1. 基本路由结构

```python
from fastapi import APIRouter, Depends
from typing import Annotated
from src.schemas import ApiResponse
from .service import MyService
from .dependencies import get_my_service

router = APIRouter(prefix="/my-module", tags=["My Module"])

@router.get(
    "/list",
    summary="获取列表",
    description="获取数据列表，支持分页"
)
async def list_items(
    service: Annotated[MyService, Depends(get_my_service)],
    page: int = 1,
    page_size: int = 20
) -> ApiResponse:
    result = await service.get_list(page, page_size)
    return ApiResponse(data=result)
```

### 2. 路由命名规范

| 操作 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 列表 | GET | `/api/v1/<module>/list` | 获取数据列表 |
| 详情 | GET | `/api/v1/<module>/get` | 获取单条数据 |
| 创建 | POST | `/api/v1/<module>/create` | 创建新数据 |
| 更新 | POST | `/api/v1/<module>/update` | 更新数据 |
| 删除 | POST | `/api/v1/<module>/delete` | 删除数据 |

### 3. 分页响应

使用 `PageResponse` 返回分页数据：

```python
from src.schemas import ApiResponse, PageResponse

@router.get("/list")
async def list_items(
    service: Annotated[MyService, Depends(get_my_service)],
    page: int = 1,
    page_size: int = 20
) -> ApiResponse[PageResponse]:
    result = await service.get_list(page, page_size)
    return ApiResponse(data=result)
```

**分页响应结构：**

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "items": [...],
        "total": 100,
        "page": 1,
        "page_size": 20
    },
    "timestamp": 1234567890
}
```

## 服务层开发规范

### 1. 服务类结构

```python
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

class MyService:
    """服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> dict:
        """获取列表"""
        # 业务逻辑实现
        pass

    async def get_by_id(self, item_id: int) -> dict:
        """获取详情"""
        # 业务逻辑实现
        pass
```

### 2. 依赖注入

在 `dependencies.py` 中定义可复用的依赖：

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

async def get_my_service(
    db: AsyncSession = Depends(get_db)
) -> MyService:
    """获取服务实例"""
    return MyService(db)

# 使用类型提示
MyServiceDep = Annotated[MyService, Depends(get_my_service)]
```

### 3. 参数验证依赖

```python
async def valid_item_id(item_id: int) -> Item:
    """验证并返回项目"""
    item = await item_service.get_by_id(item_id)
    if not item:
        raise BusinessValidationException(f"项目 {item_id} 不存在")
    return item

# 在路由中使用
@router.get("/get")
async def get_item(
    item: Annotated[Item, Depends(valid_item_id)]
) -> ApiResponse:
    return ApiResponse(data=item)
```

## 异常处理

### 自动处理

所有异常都会被全局异常处理器自动捕获并转换为 `ApiResponse` 格式：

```python
# 业务异常 - 自动转换为 400
raise BusinessValidationException("参数错误")

# HTTP 客户端异常 - 使用自定义状态码
raise HttpClientException("外部服务错误", code=503)

# 通用异常 - 自动转换为 500
raise Exception("服务器错误")
```

### 返回错误响应

```python
from src.schemas import ApiResponse, ResponseCode

# 方式 1: 抛出异常（推荐）
raise BusinessValidationException("参数错误")

# 方式 2: 直接返回错误响应
return ApiResponse.error(
    code=ResponseCode.BAD_REQUEST,
    message="参数错误"
)
```

## 文档规范

### 1. 路由文档

```python
@router.post(
    "/create",
    summary="创建项目",
    description="创建一个新的项目，返回创建的项目信息"
)
async def create_item(
    request: ItemCreate,
    service: Annotated[ItemService, Depends(get_item_service)]
) -> ApiResponse[ItemResponse]:
    """
    创建项目

    - **name**: 项目名称（必填）
    - **description**: 项目描述（可选）

    返回创建的项目信息，包含自动生成的 ID。
    """
    result = await service.create(request)
    return ApiResponse(data=result)
```

### 2. 参数文档

在 docstring 中使用 `- **param**: 描述` 格式：

```python
"""
获取项目详情

- **item_id**: 项目 ID
- **include_deleted**: 是否包含已删除的项目

返回项目的详细信息。
"""
```

## 完整示例

### schemas.py

```python
from pydantic import BaseModel
from src.schemas import ApiResponse

class ItemCreate(BaseModel):
    """创建项目请求"""
    name: str
    description: str | None = None

class ItemResponse(BaseModel):
    """项目响应"""
    id: int
    name: str
    description: str | None
```

### service.py

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.item import Item
from src.exceptions import BusinessValidationException

class ItemService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: ItemCreate) -> Item:
        """创建项目"""
        if not data.name:
            raise BusinessValidationException("项目名称不能为空")

        item = Item(**data.model_dump())
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item
```

### router.py

```python
from fastapi import APIRouter, Depends
from typing import Annotated
from src.schemas import ApiResponse
from .schemas import ItemCreate, ItemResponse
from .service import ItemService
from .dependencies import get_item_service

router = APIRouter(prefix="/items", tags=["Items"])

@router.post(
    "/create",
    summary="创建项目",
    description="创建一个新的项目"
)
async def create_item(
    request: ItemCreate,
    service: Annotated[ItemService, Depends(get_item_service)]
) -> ApiResponse[ItemResponse]:
    """
    创建项目

    - **name**: 项目名称（必填）
    - **description**: 项目描述（可选）
    """
    result = await service.create(request)
    return ApiResponse(data=result)
```

## 最佳实践

1. **始终使用 ApiResponse** - 所有路由都应返回 ApiResponse 格式
2. **使用依赖注入** - 通过 Depends 获取服务和验证参数
3. **抛出异常而非返回错误** - 使用自定义异常，让处理器统一处理
4. **添加完整的文档** - 使用 summary、description 和 docstring
5. **使用类型提示** - 为所有参数和返回值添加类型
6. **保持服务层纯净** - 服务层不处理 HTTP 相关逻辑
7. **使用 Pydantic 模型** - 请求和响应使用 Pydantic 验证
