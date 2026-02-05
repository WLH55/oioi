# 主规格文档

## 项目概述

**huobao-drama** 是一个 AI 驱动的剧本视频生成平台，用户可以通过创建剧本、分集、场景，自动生成故事板、图片和视频。

---

## 技术架构

### 技术栈

| 分类 | 技术 |
|------|------|
| 语言 | Python 3.10+ |
| Web 框架 | FastAPI + Uvicorn |
| ORM | SQLAlchemy 2.0 (异步) |
| 数据库 | SQLite (开发) / PostgreSQL (可选) |
| 数据验证 | Pydantic + Pydantic-Settings |
| 认证 | PyJWT + Passlib + python-jose |
| HTTP 客户端 | httpx + aiohttp |
| 图片处理 | Pillow |
| 视频处理 | ffmpeg-python |
| 缓存 | Redis (可选) |

### 项目结构

```
src/
├── main.py              # 应用入口
├── config.py            # 全局配置
├── database.py          # 数据库连接
├── schemas.py          # 统一响应模型
├── exceptions.py       # 自定义异常
├── exception_handlers.py # 全局异常处理
├── {模块}/             # 业务模块
│   ├── router.py       # API 路由
│   ├── service.py     # 业务逻辑
│   ├── schemas.py     # Pydantic 模型
│   ├── dependencies.py # 依赖注入
│   └── exceptions.py  # 模块异常
```

---

## 领域模型

```
Dramas (剧本)
  └── Episodes (分集)
        └── Scenes (场景)
              └── Storyboards (故事板)
                    ├── Images (图片生成)
                    └── Videos (视频生成)
```

### 核心实体

| 实体 | 说明 | 主要字段 |
|------|------|----------|
| Drama | 剧本 | title, description, status |
| Episode | 分集 | drama_id, title, content, order |
| Scene | 场景 | episode_id, description, duration |
| Storyboard | 故事板 | scene_id, frames, prompt |
| Character | 角色库 | name, appearance, voice |
| Asset | 素材库 | type, path, metadata |
| Task | 任务 | task_type, status, progress |
| AIConfig | AI 配置 | provider, model, parameters |

---

## API 设计规范

### 统一响应格式

```python
class ApiResponse(BaseModel):
    code: int = 200      # 响应码
    message: str = "success"  # 消息
    data: T | None = None    # 数据
```

### 响应码定义

| 状态码 | 常量 | 说明 |
|--------|------|------|
| 200 | SUCCESS | 成功 |
| 201 | CREATED | 已创建 |
| 400 | BAD_REQUEST | 请求参数错误 |
| 401 | UNAUTHORIZED | 未授权 |
| 403 | FORBIDDEN | 禁止访问 |
| 404 | NOT_FOUND | 资源不存在 |
| 409 | CONFLICT | 资源冲突 |
| 500 | INTERNAL_ERROR | 服务器内部错误 |
| 503 | SERVICE_UNAVAILABLE | 服务不可用 |

### 路由前缀规范

| 模块 | 路由前缀 |
|------|----------|
| Health | / |
| Settings | /api/v1/settings |
| AI Configs | /api/v1/ai-configs |
| Character Library | /api/v1/character-library |
| Assets | /api/v1/assets |
| Dramas | /api/v1/dramas |
| Episodes | /api/v1/episodes |
| Scenes | /api/v1/scenes |
| Tasks | /api/v1/tasks |
| Storyboards | /api/v1/storyboards |
| Script Generation | /api/v1/generation |
| Images | /api/v1/images |
| Videos | /api/v1/videos |
| Audio | /api/v1/audio |
| Video Merges | /api/v1/video-merges |
| Upload | /api/v1/upload |

---

## 模块规范

### 模块结构

每个业务模块应包含以下文件：

```
src/{module_name}/
├── __init__.py      # 模块导出
├── router.py        # API 路由定义
├── service.py       # 业务逻辑实现
├── schemas.py       # Pydantic 请求/响应模型
├── dependencies.py  # 依赖注入函数
└── exceptions.py    # 模块自定义异常
```

### 异常处理

- 使用 `BusinessValidationException` 进行业务参数验证
- 使用 `HttpClientException` 处理第三方 API 调用失败
- 所有异常由 `exception_handlers.py` 中的全局处理器转换为 `ApiResponse` 格式

---

## 数据库设计

### 连接配置

```python
DATABASE_TYPE: sqlite | postgresql
SQLITE_PATH: ./data/drama.db
POSTGRES_* (可选)
```

### 异步会话管理

```python
# 依赖注入获取会话
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
        await session.commit()
```

---

## 配置管理

所有配置通过 `Settings` 类管理，支持环境变量覆盖：

```python
# 应用配置
APP_NAME: str
APP_VERSION: str
DEBUG: bool

# 服务器配置
HOST: str
PORT: int

# CORS 配置
CORS_ORIGINS: list[str]

# 存储配置
STORAGE_TYPE: local
LOCAL_STORAGE_PATH: str

# AI 配置
DEFAULT_AI_PROVIDER: str
```

---

## 编码规范

### 命名约定

- **文件**: 小写下划线 `snake_case`
- **类**: 大驼峰 `PascalCase`
- **函数/变量**: 小写下划线 `snake_case`
- **常量**: 全大写下划线 `UPPER_SNAKE_CASE`

### 函数注释

```python
def function_name(param: Type) -> ReturnType:
    """
    函数简短描述

    Args:
        param: 参数说明

    Returns:
        返回值说明

    Raises:
        ExceptionType: 异常说明
    """
```

---

## 测试规范

### 测试文件位置

```
tests/
├── conftest.py
├── {模块}/
│   └── test_{模块}.py
```

---

## 部署配置

### Docker 支持

- `Dockerfile`: 应用容器化
- `docker-compose.yml`: 本地开发环境

### 启动命令

```bash
# 开发模式
uvicorn src.main:app --reload

# 生产模式
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

---

## 历史变更

| 变更 ID | 日期 | 描述 |
|---------|------|------|
| 2025-02-05-refactor-project-structure | 2026-02-04 | 重构项目结构，迁移到模块化单体架构 |
