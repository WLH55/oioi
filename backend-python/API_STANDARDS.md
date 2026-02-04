# API 规范文档

本文档定义了项目中所有 API 接口必须遵循的统一规范。

## 目录

- [统一响应格式](#统一响应格式)
- [响应码定义](#响应码定义)
- [路由规范](#路由规范)
- [异常处理](#异常处理)
- [接口文档要求](#接口文档要求)
- [使用示例](#使用示例)

---

## 统一响应格式

所有 API 接口必须返回统一的 JSON 格式：

```json
{
    "code": 200,
    "message": "success",
    "data": {...}
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | int | 响应码，200 表示成功 |
| `message` | str | 响应消息 |
| `data` | any | 响应数据，成功时返回具体数据，失败时为 null |

### 成功响应示例

```json
{
    "code": 200,
    "message": "操作成功",
    "data": {
        "id": 1,
        "name": "示例数据"
    }
}
```

### 错误响应示例

```json
{
    "code": 400,
    "message": "参数验证失败",
    "data": null
}
```

---

## 响应码定义

使用 `src.schemas.ResponseCode` 类中定义的常量：

```python
from src.schemas import ResponseCode

# 成功
ResponseCode.SUCCESS = 200
ResponseCode.CREATED = 201

# 客户端错误
ResponseCode.BAD_REQUEST = 400
ResponseCode.UNAUTHORIZED = 401
ResponseCode.FORBIDDEN = 403
ResponseCode.NOT_FOUND = 404
ResponseCode.CONFLICT = 409

# 服务器错误
ResponseCode.INTERNAL_ERROR = 500
ResponseCode.SERVICE_UNAVAILABLE = 503
```

---

## 路由规范

### HTTP 方法

**仅使用 `GET` 和 `POST` 两种方法：**

| 方法 | 用途 | 示例 |
|------|------|------|
| `GET` | 查询资源 | `/users/info`、`/users/list` |
| `POST` | 创建/操作资源 | `/users/create`、`/users/update`、`/users/delete` |

### 路由命名

遵循 `/模块/操作` 格式：

```
GET  /dramas/info       # 获取单个剧目
GET  /dramas/list       # 获取剧目列表
POST /dramas/create     # 创建剧目
POST /dramas/update     # 更新剧目
POST /dramas/delete     # 删除剧目
```

### 分页参数

列表接口统一使用以下分页参数：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `page` | int | 1 | 页码，从 1 开始 |
| `page_size` | int | 10 | 每页数量，最大 100 |

分页响应格式：

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "list": [...],
        "total": 100,
        "page": 1,
        "page_size": 10
    }
}
```

---

## 异常处理

### 自定义异常

#### BusinessValidationException

业务参数验证异常，用于请求参数不符合业务规则。

```python
from src.exceptions import BusinessValidationException

if quantity <= 0:
    raise BusinessValidationException("数量必须大于 0")
```

响应：

```json
{
    "code": 400,
    "message": "数量必须大于 0",
    "data": null
}
```

#### HttpClientException

第三方 API 调用失败异常。

```python
from src.exceptions import HttpClientException

try:
    response = await external_api_call()
except Exception as e:
    raise HttpClientException("AI 服务调用失败", code=503)
```

---

## 接口文档要求

### 必需元素

所有接口必须包含：

1. **`summary`**: 简短描述
2. **`response_model`**: 响应模型（`ApiResponse`）
3. **函数 docstring**: 详细说明

### 示例

```python
from fastapi import APIRouter, Query
from src.schemas import ApiResponse
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])


class CreateUserRequest(BaseModel):
    """创建用户请求"""
    name: str
    email: str


@router.post("/create", summary="创建用户", response_model=ApiResponse)
async def create_user(request: CreateUserRequest) -> ApiResponse:
    """
    创建新用户

    Args:
        request: 创建用户请求，包含用户名和邮箱

    Returns:
        ApiResponse: 创建结果，包含用户 ID
    """
    # 业务逻辑...
    return ApiResponse.success(data={"id": 123}, message="用户创建成功")
```

---

## 使用示例

### 完整的 CRUD 接口示例

```python
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import List, Optional

from src.schemas import ApiResponse, ResponseCode
from src.exceptions import BusinessValidationException

router = APIRouter(prefix="/dramas", tags=["dramas"])


# ========== 请求模型 ==========

class CreateDramaRequest(BaseModel):
    """创建剧目请求"""
    title: str = Field(..., min_length=1, max_length=200, description="剧目标题")
    description: str = Field(default="", description="剧目描述")


# ========== GET 接口 ==========

@router.get("/info", summary="获取剧目信息", response_model=ApiResponse)
async def get_drama_info(
    drama_id: int = Query(..., description="剧目 ID")
) -> ApiResponse:
    """
    获取指定剧目的详细信息

    Args:
        drama_id: 剧目 ID

    Returns:
        ApiResponse: 剧目信息
    """
    # 查询逻辑...
    drama = {"id": drama_id, "title": "示例剧目"}
    return ApiResponse.success(data=drama)


@router.get("/list", summary="获取剧目列表", response_model=ApiResponse)
async def get_drama_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量")
) -> ApiResponse:
    """
    获取剧目列表（分页）

    Args:
        page: 页码
        page_size: 每页数量

    Returns:
        ApiResponse: 剧目列表
    """
    # 查询逻辑...
    dramas = [{"id": 1, "title": "剧目1"}]
    total = 100

    return ApiResponse.success(data={
        "list": dramas,
        "total": total,
        "page": page,
        "page_size": page_size
    })


# ========== POST 接口 ==========

@router.post("/create", summary="创建剧目", response_model=ApiResponse)
async def create_drama(request: CreateDramaRequest) -> ApiResponse:
    """
    创建新剧目

    Args:
        request: 创建剧目请求

    Returns:
        ApiResponse: 创建结果
    """
    # 参数验证
    if len(request.title) < 2:
        raise BusinessValidationException("剧目标题至少需要 2 个字符")

    # 创建逻辑...
    drama = {"id": 1, "title": request.title}

    return ApiResponse.success(data=drama, message="剧目创建成功")


@router.post("/update", summary="更新剧目", response_model=ApiResponse)
async def update_drama(
    drama_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> ApiResponse:
    """
    更新剧目信息

    Args:
        drama_id: 剧目 ID
        title: 新标题（可选）
        description: 新描述（可选）

    Returns:
        ApiResponse: 更新结果
    """
    # 更新逻辑...
    return ApiResponse.success(message="剧目更新成功")


@router.post("/delete", summary="删除剧目", response_model=ApiResponse)
async def delete_drama(drama_id: int) -> ApiResponse:
    """
    删除指定剧目

    Args:
        drama_id: 剧目 ID

    Returns:
        ApiResponse: 删除结果
    """
    # 删除逻辑...
    return ApiResponse.success(message="剧目删除成功")
```

### 分页接口示例

```python
@router.get("/list", summary="获取列表", response_model=ApiResponse[dict])
async def get_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量")
) -> ApiResponse[dict]:
    """
    获取分页列表

    Args:
        page: 页码
        page_size: 每页数量

    Returns:
        ApiResponse: 包含 list、total、page、page_size 的数据
    """
    items = [...]  # 查询数据
    total = 100   # 总数

    return ApiResponse.success(data={
        "list": items,
        "total": total,
        "page": page,
        "page_size": page_size
    })
```

### 异常处理示例

```python
from src.exceptions import BusinessValidationException, HttpClientException


@router.post("/submit", summary="提交订单", response_model=ApiResponse)
async def submit_order(request: CreateOrderRequest) -> ApiResponse:
    """
    提交订单

    可能抛出:
        BusinessValidationException: 参数验证失败
        HttpClientException: 第三方服务调用失败
    """
    # 参数验证
    if request.quantity <= 0:
        raise BusinessValidationException("数量必须大于 0")

    if request.quantity > 100:
        raise BusinessValidationException("单次下单数量不能超过 100")

    # 调用第三方服务
    try:
        result = await external_service.create_order(...)
    except Exception as e:
        raise HttpClientException(f"订单服务调用失败: {str(e)}", code=503)

    return ApiResponse.success(data=result, message="订单提交成功")
```

---

## 迁移检查清单

在迁移现有接口时，确保：

- [ ] 使用 `GET` 或 `POST` 方法
- [ ] 路由路径遵循 `/模块/操作` 格式
- [ ] 使用 Pydantic Model 定义请求参数
- [ ] 添加 `response_model=ApiResponse` 类型提示
- [ ] 使用 `ApiResponse.success()` 返回成功响应
- [ ] 抛出 `BusinessValidationException` 处理参数错误
- [ ] 抛出 `HttpClientException` 处理第三方 API 错误
- [ ] 添加 `summary` 和完整的 docstring
