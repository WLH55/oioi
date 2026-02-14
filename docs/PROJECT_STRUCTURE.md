# 项目结构说明文档

## 概述

本项目采用模块化的项目结构，将代码组织在 `src/` 目录下，每个模块独立管理路由、服务、数据模型等。

## 目录结构

```
backend-python/
├── src/                        # 源代码目录
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 全局配置
│   ├── database.py             # 数据库连接
│   ├── schemas.py              # 统一响应模式
│   ├── exceptions.py           # 自定义异常
│   ├── exception_handlers.py   # 全局异常处理器
│   │
│   ├── health/                 # 健康检查模块
│   ├── settings/               # 系统设置模块
│   ├── ai_configs/             # AI 配置模块
│   ├── character_library/      # 角色库模块
│   ├── assets/                 # 资产管理模块
│   ├── dramas/                 # 剧目管理模块
│   ├── episodes/               # 集数管理模块
│   ├── scenes/                 # 场景管理模块
│   ├── tasks/                  # 任务管理模块
│   ├── storyboards/            # 分镜管理模块
│   ├── script_generation/      # 剧本生成模块
│   ├── images/                 # 图片生成模块
│   ├── audio/                  # 音频处理模块
│   ├── videos/                 # 视频生成模块
│   ├── video_merges/           # 视频合成模块
│   ├── upload/                 # 文件上传模块
│   │
│   ├── ai/                     # AI 服务共享模块
│   │   ├── client.py           # AI 客户端基类
│   │   └── factory.py          # AI 提供商工厂
│   │
│   └── utils/                  # 工具函数
│
├── app/                        # 旧代码（保留中）
│   ├── core/                   # 核心配置
│   ├── middlewares/            # 中间件
│   ├── models/                 # 数据库模型
│   └── services/               # AI 服务实现
│
├── tests/                      # 测试目录
│   ├── conftest.py             # 测试配置
│   ├── health/                 # 健康检查测试
│   ├── settings/               # 设置测试
│   └── ...                     # 其他模块测试
│
├── requirements/               # 依赖管理
│   ├── base.txt                # 基础依赖
│   ├── dev.txt                 # 开发依赖
│   └── prod.txt                # 生产依赖
│
├── local_storage/              # 本地存储
├── data/                       # 数据目录
├── logs/                       # 日志目录
│
├── pyproject.toml              # 项目配置
├── Dockerfile                  # Docker 配置
├── docker-compose.yml          # Docker Compose
├── start.bat                   # Windows 启动脚本
└── start.sh                    # Linux/Mac 启动脚本
```

## 模块结构规范

每个业务模块遵循以下结构：

```
<module_name>/
├── __init__.py             # 模块导出
├── router.py               # 路由定义
├── service.py              # 业务逻辑
├── schemas.py              # 请求/响应模式
├── dependencies.py         # 依赖注入
├── exceptions.py           # 模块异常
├── config.py               # 模块配置
├── constants.py            # 常量定义
└── tasks.py                # 异步任务（可选）
```

## 模块职责

### API 层 (router.py)
- 定义 FastAPI 路由
- 处理 HTTP 请求/响应
- 使用依赖注入获取服务
- 返回统一的 ApiResponse 格式

### 业务层 (service.py)
- 实现核心业务逻辑
- 处理数据验证和转换
- 调用外部服务（AI、数据库等）
- 不直接处理 HTTP 相关逻辑

### 数据层
- 模型定义在 `app/models/`
- 数据库操作使用 SQLAlchemy 异步会话
- 模型与业务逻辑分离

### 依赖注入 (dependencies.py)
- 定义可复用的依赖项
- 实现参数验证（如 valid_drama_id）
- 缓存常用数据

## API 响应规范

所有 API 端点返回统一的 `ApiResponse` 格式：

```python
{
    "code": 200,           # 响应码
    "message": "success",  # 响应消息
    "data": {...},         # 响应数据
    "timestamp": 1234567890
}
```

## 异常处理规范

- 使用 `BusinessValidationException` 处理业务验证错误
- 使用 `HttpClientException` 处理外部 API 调用错误
- 所有异常通过全局处理器转换为 ApiResponse 格式

## 路由命名规范

- 列表: `GET /api/v1/<module>/list`
- 详情: `GET /api/v1/<module>/get`
- 创建: `POST /api/v1/<module>/create`
- 更新: `POST /api/v1/<module>/update`
- 删除: `POST /api/v1/<module>/delete`

## 分页参数规范

所有列表接口使用统一的分页参数：

- `page`: 页码（默认 1）
- `page_size`: 每页数量（默认 20）

返回格式使用 `PageResponse`：

```python
{
    "items": [...],        # 数据列表
    "total": 100,          # 总数
    "page": 1,             # 当前页
    "page_size": 20        # 每页数量
}
```

## 迁移状态

### 已迁移到 src/
- ✅ health
- ✅ settings
- ✅ ai_configs
- ✅ character_library
- ✅ assets
- ✅ dramas
- ✅ episodes
- ✅ scenes
- ✅ tasks
- ✅ storyboards
- ✅ script_generation
- ✅ images
- ✅ audio
- ✅ videos
- ✅ video_merges
- ✅ upload

### 保留在 app/
- `app/core/` - 核心配置（数据库 Base）
- `app/models/` - 数据库模型
- `app/middlewares/` - 中间件
- `app/services/` - AI 服务实现

## 开发指南

1. **添加新模块**
   - 在 `src/` 下创建模块目录
   - 遵循模块结构规范
   - 在 `src/main.py` 中注册路由

2. **编写测试**
   - 在 `tests/` 下创建对应目录
   - 使用 pytest 和异步测试客户端
   - 测试文件命名: `test_<module>.py`

3. **代码风格**
   - 使用 ruff 进行代码检查
   - 运行 `ruff check src/ --fix` 自动修复

4. **运行项目**
   - Windows: `start.bat`
   - Linux/Mac: `./start.sh`
   - 或直接: `python -m src.main`
