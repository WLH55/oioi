# 统一响应模型与路由规范

> FastAPI 项目的 API 响应格式标准

---

## 一、统一响应格式

### 响应结构

所有 API 接口返回统一的 JSON 格式：

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

---

## 二、ApiResponse 泛型响应模型

### 模型定义

```python
# app/schemas.py
from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """
    统一 API 响应格式

    Attributes:
        code: 响应码
        message: 响应消息
        data: 响应数据（泛型）
    """
    code: int = Field(200, description="响应码")
    message: str = Field("success", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")

    @classmethod
    def success(cls, data: Any = None, message: str = "success") -> "ApiResponse[T]":
        """
        成功响应

        Args:
            data: 响应数据
            message: 成功消息

        Returns:
            ApiResponse: 成功响应实例
        """
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, code: int, message: str, data: Any = None) -> "ApiResponse[T]":
        """
        错误响应

        Args:
            code: 错误码
            message: 错误消息
            data: 附加数据

        Returns:
            ApiResponse: 错误响应实例
        """
        return cls(code=code, message=message, data=data)
```

### 使用示例

#### 示例 1：返回简单数据

```python
from fastapi import APIRouter
from app.schemas import ApiResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/info", response_model=ApiResponse)
async def get_user_info(user_id: int):
    """获取用户信息"""
    user_data = {
        "id": user_id,
        "name": "Alice",
        "email": "alice@example.com"
    }
    return ApiResponse.success(data=user_data)
```

**响应：**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "name": "Alice",
        "email": "alice@example.com"
    }
}
```

#### 示例 2：返回列表数据

```python
@router.get("/list", response_model=ApiResponse)
async def get_user_list():
    """获取用户列表"""
    users = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
        {"id": 3, "name": "Charlie"}
    ]
    return ApiResponse.success(data=users, message="获取成功")
```

**响应：**
```json
{
    "code": 200,
    "message": "获取成功",
    "data": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
        {"id": 3, "name": "Charlie"}
    ]
}
```

#### 示例 3：泛型类型提示

```python
from typing import List
from pydantic import BaseModel


class User(BaseModel):
    """用户数据模型"""
    id: int
    name: str


@router.get("/typed", response_model=ApiResponse[List[User]])
async def get_users_typed():
    """获取用户列表（带类型提示）"""
    users = [
        User(id=1, name="Alice"),
        User(id=2, name="Bob")
    ]
    return ApiResponse.success(data=users)
```

---

## 三、ResponseCode 响应码常量

### 响应码定义

```python
# app/schemas.py
class ResponseCode:
    """
    响应码常量

    遵循 HTTP 标准错误码规范
    """
    # ========== 成功 ==========
    SUCCESS = 200           # 成功
    CREATED = 201           # 已创建

    # ========== 客户端错误 ==========
    BAD_REQUEST = 400       # 请求参数错误
    UNAUTHORIZED = 401      # 未授权
    FORBIDDEN = 403         # 禁止访问
    NOT_FOUND = 404         # 资源不存在
    CONFLICT = 409          # 资源冲突

    # ========== 服务器错误 ==========
    INTERNAL_ERROR = 500    # 服务器内部错误
    SERVICE_UNAVAILABLE = 503  # 服务不可用
```

### 使用示例

```python
from app.schemas import ApiResponse, ResponseCode

# 成功响应
return ApiResponse.success(data=user_data)

# 错误响应
return ApiResponse.error(
    code=ResponseCode.NOT_FOUND,
    message="用户不存在"
)
```

---

## 四、异常处理

### 自定义异常类

```python
# app/exceptions.py
from typing import Optional


class HttpClientException(Exception):
    """
    HTTP 客户端异常

    用于第三方 API 调用失败
    """
    def __init__(self, message: str, code: Optional[int] = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class BusinessValidationException(Exception):
    """
    业务参数验证异常

    用于请求参数不符合业务规则
    """
    def __init__(self, message: str, code: Optional[int] = None):
        self.message = message
        self.code = code
        super().__init__(self.message)
```

### 异常处理器

```python
# app/exceptions.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.schemas import ApiResponse, ResponseCode


async def validation_exception_handler(request: Request, exc: BusinessValidationException) -> JSONResponse:
    """处理业务参数验证异常"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ApiResponse.error(
            code=ResponseCode.BAD_REQUEST,
            message=exc.message or "参数验证失败"
        ).model_dump()
    )


async def httpclient_exception_handler(request: Request, exc: HttpClientException) -> JSONResponse:
    """处理 HTTP 客户端异常"""
    return JSONResponse(
        status_code=exc.code or status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ApiResponse.error(
            code=exc.code or ResponseCode.INTERNAL_ERROR,
            message=exc.message
        ).model_dump()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理所有未捕获的异常"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ApiResponse.error(
            code=ResponseCode.INTERNAL_ERROR,
            message=str(exc) or "服务器内部错误"
        ).model_dump()
    )
```

### 注册异常处理器

```python
# app/main.py
from app.exceptions import register_exception_handlers

def create_app() -> FastAPI:
    app = FastAPI()

    # 注册全局异常处理器
    register_exception_handlers(app)

    return app
```

```python
# app/exceptions.py
def register_exception_handlers(app) -> None:
    """注册全局异常处理器"""
    app.add_exception_handler(BusinessValidationException, validation_exception_handler)
    app.add_exception_handler(HttpClientException, httpclient_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
```

### 异常使用示例

```python
from fastapi import APIRouter
from app.schemas import ApiResponse, ResponseCode
from app.exceptions import BusinessValidationException

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/create", response_model=ApiResponse)
async def create_order(product_id: int, quantity: int):
    """创建订单"""

    # 参数验证
    if quantity <= 0:
        raise BusinessValidationException("数量必须大于 0")

    if quantity > 100:
        raise BusinessValidationException("单次下单数量不能超过 100")

    # 业务逻辑...
    order = {"id": 123, "product_id": product_id, "quantity": quantity}

    return ApiResponse.success(data=order, message="订单创建成功")
```

**错误响应（参数验证失败）：**
```json
{
    "code": 400,
    "message": "数量必须大于 0",
    "data": null
}
```

---

## 五、路由规范

### 路由方法规范

| 方法 | 用途 | 示例 |
|------|------|------|
| `GET` | 查询资源 | `/users/info`、`/users/list` |
| `POST` | 创建/操作资源 | `/users/create`、`/orders/submit` |

> **规范约定**：仅使用 GET 和 POST 两种方法

### 路由命名规范

```
/模块/操作

示例：
GET  /users/info       # 获取用户信息
GET  /users/list       # 获取用户列表
POST /users/create     # 创建用户
POST /users/update     # 更新用户
POST /users/delete     # 删除用户
```

### 路由完整示例

```python
# app/routers/users.py
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Query

from app.schemas import ApiResponse, ResponseCode
from app.dependencies import UserClientDep


router = APIRouter(prefix="/users", tags=["users"])


# ========== 请求模型 ==========

class CreateUserRequest(BaseModel):
    """创建用户请求"""
    name: str = Field(..., min_length=1, max_length=50, description="用户名")
    email: str = Field(..., description="邮箱")
    age: int = Field(default=0, ge=0, le=150, description="年龄")


# ========== GET 接口 ==========

@router.get("/info", summary="获取用户信息", response_model=ApiResponse)
async def get_user_info(
    user_id: int = Query(..., description="用户ID")
) -> ApiResponse:
    """
    获取用户信息

    Args:
        user_id: 用户ID

    Returns:
        ApiResponse: 用户信息
    """
    # 查询逻辑...
    user = {
        "id": user_id,
        "name": "Alice",
        "email": "alice@example.com",
        "age": 25
    }
    return ApiResponse.success(data=user)


@router.get("/list", summary="获取用户列表", response_model=ApiResponse)
async def get_user_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量")
) -> ApiResponse:
    """
    获取用户列表

    Args:
        page: 页码
        page_size: 每页数量

    Returns:
        ApiResponse: 用户列表
    """
    # 查询逻辑...
    users = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]
    total = 100

    return ApiResponse.success(data={
        "list": users,
        "total": total,
        "page": page,
        "page_size": page_size
    })


# ========== POST 接口 ==========

@router.post("/create", summary="创建用户", response_model=ApiResponse)
async def create_user(
    request: CreateUserRequest,
    client: UserClientDep
) -> ApiResponse:
    """
    创建用户

    Args:
        request: 创建用户请求
        client: 用户客户端（依赖注入）

    Returns:
        ApiResponse: 创建结果
    """
    # 参数验证
    if request.age < 18:
        raise BusinessValidationException("年龄必须大于等于 18 岁")

    # 调用客户端
    data = request.model_dump()
    result = await client.create_user(data)

    return ApiResponse.success(data=result, message="用户创建成功")


@router.post("/update", summary="更新用户", response_model=ApiResponse)
async def update_user(
    user_id: int,
    name: Optional[str] = None,
    email: Optional[str] = None
) -> ApiResponse:
    """
    更新用户

    Args:
        user_id: 用户ID
        name: 用户名（可选）
        email: 邮箱（可选）

    Returns:
        ApiResponse: 更新结果
    """
    # 更新逻辑...
    return ApiResponse.success(message="用户更新成功")


@router.post("/delete", summary="删除用户", response_model=ApiResponse)
async def delete_user(user_id: int) -> ApiResponse:
    """
    删除用户

    Args:
        user_id: 用户ID

    Returns:
        ApiResponse: 删除结果
    """
    # 删除逻辑...
    return ApiResponse.success(message="用户删除成功")
```

---

## 六、完整流程示例

### 场景：用户下单接口

```python
# app/routers/orders.py
from pydantic import BaseModel, Field
from fastapi import APIRouter
from app.schemas import ApiResponse, ResponseCode
from app.exceptions import BusinessValidationException
from app.dependencies import OrderClientDep


router = APIRouter(prefix="/orders", tags=["orders"])


# ========== 请求模型 ==========

class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    product_id: int = Field(..., description="商品ID")
    quantity: int = Field(..., gt=0, le=100, description="数量")
    remark: str = Field(default="", description="备注")


# ========== 接口实现 ==========

@router.post("/submit", summary="提交订单", response_model=ApiResponse)
async def submit_order(
    request: CreateOrderRequest,
    client: OrderClientDep
) -> ApiResponse:
    """
    提交订单

    流程：
    1. 参数验证
    2. 库存检查
    3. 调用第三方 API
    4. 返回统一格式响应

    Args:
        request: 订单请求
        client: 订单客户端

    Returns:
        ApiResponse: 订单信息
    """
    # ========== 1. 参数验证 ==========
    if request.quantity < 1:
        raise BusinessValidationException("购买数量不能少于 1")

    if request.quantity > 100:
        raise BusinessValidationException("单次购买数量不能超过 100")

    # ========== 2. 业务逻辑 ==========
    # 检查库存...
    stock = await client.check_stock(request.product_id)
    if stock < request.quantity:
        raise BusinessValidationException(f"库存不足，当前库存: {stock}")

    # ========== 3. 调用第三方 API ==========
    order_data = {
        "product_id": request.product_id,
        "quantity": request.quantity,
        "remark": request.remark
    }
    result = await client.create_order(order_data)

    # ========== 4. 返回统一响应 ==========
    return ApiResponse.success(
        data={
            "order_id": result["order_id"],
            "total_amount": result["amount"],
            "status": "pending"
        },
        message="订单提交成功"
    )
```

**成功响应：**
```json
{
    "code": 200,
    "message": "订单提交成功",
    "data": {
        "order_id": "ORD20240203123456",
        "total_amount": 299.00,
        "status": "pending"
    }
}
```

**错误响应（库存不足）：**
```json
{
    "code": 400,
    "message": "库存不足，当前库存: 5",
    "data": null
}
```

---

## 七、快速检查清单

### 编写路由时检查

- [ ] 使用 `GET` 或 `POST` 方法
- [ ] 路由路径遵循 `/模块/操作` 格式
- [ ] 使用 Pydantic Model 定义请求参数
- [ ] 添加 `response_model=ApiResponse` 类型提示
- [ ] 使用 `ApiResponse.success()` 返回成功响应
- [ ] 抛出 `BusinessValidationException` 处理参数错误
- [ ] 添加 docstring 说明参数和返回值

### 编写客户端时检查

- [ ] 抛出 `HttpClientException` 处理 API 调用失败
- [ ] 异常包含有意义的 `message` 和正确的 `code`
- [ ] 返回第三方 API 原始响应，由路由层封装

---

## 八、文件结构

```
app/
├── schemas.py              # ApiResponse + ResponseCode
├── exceptions.py           # 异常类 + 异常处理器
├── dependencies.py         # 依赖注入
├── routers/
│   └── module.py          # 路由接口
└── main.py                # 注册异常处理器
```
