## Why

当前项目存在以下问题，需要重构：

**1. 项目结构不符合 FastAPI 最佳实践**
项目采用按文件类型划分的方式（如 `routes/`, `models/`, `schemas/`, `services/`），这种方式在微服务或小型项目中尚可，但随着项目规模增长和领域模块增多，这种结构会导致：
- 相关代码分散在多个目录中，难以维护
- 模块边界不清晰，容易产生耦合
- 新增功能时需要在多个目录间切换
- 不利于团队协作和代码复用

**2. API 响应格式不统一**
当前项目缺少统一的 API 响应规范，导致：
- 不同接口返回格式不一致
- 错误处理方式不统一
- 客户端需要处理多种响应格式
- 缺少统一的响应码管理

**3. 路由定义不规范**
- 路由方法使用不一致（混用 GET/POST/PUT/DELETE）
- 路由命名不统一
- 缺少统一的请求参数验证规范
- 接口文档不完善

参考 [Netflix Dispatch](https://github.com/Netflix/dispatch) 的结构模式，采用按领域/业务模块划分的方式，并建立统一的 API 规范，可以提高项目的可维护性和可扩展性。

## What Changes

**项目结构重构**：
- **BREAKING**: 将 `app/` 目录重构为 `src/` 目录
- **BREAKING**: 将所有代码从按文件类型划分改为按业务领域模块划分
- **BREAKING**: 重新组织导入路径，所有导入需要使用新的路径结构
- 每个业务模块（如 `dramas`, `episodes`, `tasks` 等）将拥有独立的目录，包含：
  - `router.py` - 路由定义
  - `schemas.py` - Pydantic 模型
  - `models.py` - 数据库模型
  - `dependencies.py` - 依赖项
  - `service.py` - 业务逻辑
  - `config.py` - 模块配置
  - `constants.py` - 常量和错误码
  - `exceptions.py` - 模块特定异常
  - `utils.py` - 工具函数
- 全局配置和共享模块保留在 `src/` 根目录
- 依赖管理从 `requirements.txt` 改为分层结构 `requirements/base.txt`, `dev.txt`, `prod.txt`
- 测试目录按模块组织在 `tests/` 下

**API 响应标准化**：
- **BREAKING**: 所有 API 接口必须返回统一的 `ApiResponse` 格式
- 新增 `ApiResponse` 泛型响应模型（包含 code, message, data 字段）
- 新增 `ResponseCode` 响应码常量类
- 统一异常处理机制
- **BREAKING**: 所有路由接口的 `response_model` 必须使用 `ApiResponse`

**路由规范化**：
- **BREAKING**: 仅使用 `GET` 和 `POST` 两种 HTTP 方法
- **BREAKING**: 路由命名统一为 `/模块/操作` 格式
- 统一使用 Pydantic Model 定义请求参数
- 所有接口添加 `summary` 和 `description` 文档
- 统一分页参数规范（page, page_size）

## Capabilities

### New Capabilities
- `modular-project-structure`: 实现按领域模块划分的项目结构
- `module-isolation`: 每个模块拥有独立的配置、依赖、常量和异常定义
- `dependency-injection`: 使用 FastAPI 依赖系统进行模块间通信和验证
- `separate-configs`: 将 Pydantic BaseSettings 按模块解耦
- `async-tests`: 配置异步测试客户端和测试环境
- `unified-api-response`: 统一 API 响应格式和响应码
- `standardized-routes`: 标准化路由方法和命名规范
- `exception-handling`: 统一异常处理机制

### Modified Capabilities
所有现有 API 接口的行为（返回格式、路由方法）都将改变，需要更新客户端调用方式

## Impact

**受影响的代码**：
- 所有现有文件的路径都将改变
- 所有导入语句需要更新
- `main.py` 需要更新路由导入路径
- 配置文件需要重新组织
- **所有路由接口需要重写以符合新的响应格式和规范**
- **所有客户端调用代码需要适配新的响应格式**

**受影响的 API**：
- **所有现有 API 接口的响应格式将改变**（从直接返回数据改为 `{code, message, data}` 格式）
- **路由方法可能改变**（PUT/DELETE 改为 POST）
- **路由路径可能改变**（统一为 `/模块/操作` 格式）

**受影响的系统**：
- 开发环境启动脚本
- 部署配置
- CI/CD 管道中的路径引用
- **所有调用后端 API 的前端应用**

**依赖项**：
- 可能需要添加测试依赖（如 httpx 用于异步测试）
- ruff 用于代码格式化和检查

**迁移策略**：
1. 先创建新的 `src/` 结构
2. 实现统一的 `ApiResponse` 和异常处理机制
3. 逐个迁移模块，确保每个模块迁移后测试通过
4. 更新所有前端调用代码适配新的响应格式
5. 最后删除旧的 `app/` 目录
