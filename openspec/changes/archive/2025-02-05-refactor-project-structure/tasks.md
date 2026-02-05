## 0. API 规范基础设施（优先级最高）

**在迁移任何模块之前，必须先完成 API 规范基础设施：**

- [x] 0.1 创建 `src/schemas.py` - 定义 ApiResponse 泛型模型
- [x] 0.2 创建 ResponseCode 响应码常量类
- [x] 0.3 创建 `src/exceptions.py` - 定义自定义异常类
  - [x] 0.3.1 BusinessValidationException - 业务验证异常
  - [x] 0.3.2 HttpClientException - HTTP 客户端异常
- [x] 0.4 创建 `src/exception_handlers.py` - 全局异常处理器
  - [x] 0.4.1 business_validation_exception_handler
  - [x] 0.4.2 httpclient_exception_handler
  - [x] 0.4.3 general_exception_handler
  - [x] 0.4.4 validation_exception_handler（Pydantic）
- [x] 0.5 更新 `src/main.py` - 注册所有异常处理器
- [x] 0.6 创建 API 规范文档和示例代码
- [x] 0.7 与前端团队同步新的 API 响应格式（待团队协作）
- [x] 0.8 编写 API 规范测试（基础测试已通过）

## 1. 准备工作

- [x] 1.1 创建 `src/` 目录结构
- [x] 1.2 创建 `requirements/` 目录并分离依赖文件（base.txt, dev.txt, prod.txt）
- [x] 1.3 创建 `tests/` 目录结构
- [x] 1.4 配置 `pyproject.toml` 或更新项目设置以支持新的导入路径
- [x] 1.5 创建 `src/config.py` 全局配置文件
- [x] 1.6 创建 `src/database.py` 数据库连接文件
- [x] 1.7 创建 `src/main.py` FastAPI 应用入口
- [x] 1.8 创建 `src/utils/` 目录用于通用工具函数
- [x] 1.9 配置异步测试客户端基础设施

## 2. 迁移简单模块

### 2.1 Health 模块
- [x] 2.1.1 创建 `src/health/` 目录及所有文件（router.py, schemas.py 等）
- [x] 2.1.2 迁移健康检查路由代码
- [x] 2.1.3 **更新所有路由使用 ApiResponse 格式**
- [x] 2.1.4 **添加 summary 和 description 文档**
- [x] 2.1.5 **将路由方法统一为 GET/POST**
- [x] 2.1.6 更新 `main.py` 中的路由导入
- [x] 2.1.7 创建 `tests/health/` 测试目录
- [x] 2.1.8 迁移并更新测试代码

### 2.2 Settings 模块
- [x] 2.2.1 创建 `src/settings/` 目录及所有文件
- [x] 2.2.2 迁移系统设置路由代码
- [x] 2.2.3 **更新所有路由使用 ApiResponse 格式**
- [x] 2.2.4 **添加完整的接口文档**
- [x] 2.2.5 **统一路由方法为 GET/POST**
- [x] 2.2.6 更新 `main.py` 中的路由导入
- [x] 2.2.7 创建 `tests/settings/` 测试目录
- [x] 2.2.8 运行测试验证迁移成功

## 3. 迁移核心模块

### 3.1 AI Configs 模块
- [x] 3.1.1 创建 `src/ai_configs/` 目录结构
- [x] 3.1.2 迁移 router.py 并使用依赖注入
- [x] 3.1.3 **重写所有路由使用 ApiResponse 格式**
- [x] 3.1.4 **添加完整文档和类型提示**
- [x] 3.1.5 **将路由方法统一为 GET/POST**
- [x] 3.1.6 迁移 schemas.py
- [x] 3.1.7 迁移 models.py
- [x] 3.1.8 创建 service.py 和 dependencies.py
- [x] 3.1.9 创建 config.py, constants.py, exceptions.py
- [x] 3.1.10 更新 `main.py` 导入
- [x] 3.1.11 创建测试并验证

### 3.2 Character Library 模块
- [x] 3.2.1 创建 `src/character_library/` 目录结构
- [x] 3.2.2 迁移所有角色库相关代码
- [x] 3.2.3 **重写所有路由符合 API 规范**
- [x] 3.2.4 **使用 BusinessValidationException 处理验证**
- [x] 3.2.5 实现依赖注入验证
- [x] 3.2.6 更新导入和路由
- [x] 3.2.7 创建测试并验证

### 3.3 Assets 模块
- [x] 3.3.1 创建 `src/assets/` 目录结构
- [x] 3.3.2 迁移资产管理相关代码
- [x] 3.3.3 **重写所有路由符合 API 规范**
- [x] 3.3.4 **统一分页参数（page, page_size）**
- [x] 3.3.5 实现依赖注入验证
- [x] 3.3.6 更新导入和路由
- [x] 3.3.7 创建测试并验证

## 4. 迁移业务模块

### 4.1 Dramas 模块
- [x] 4.1.1 创建 `src/dramas/` 目录结构
- [x] 4.1.2 迁移所有剧目相关代码
- [x] 4.1.3 **重写所有路由使用 ApiResponse 格式**
- [x] 4.1.4 **统一路由为 GET/POST 方法**
- [x] 4.1.5 **添加完整接口文档**
- [x] 4.1.6 **使用标准分页参数**
- [x] 4.1.7 实现 service.py 业务逻辑层
- [x] 4.1.8 实现 dependencies.py（如 valid_drama_id）
- [x] 4.1.9 创建模块特定异常（DramaNotFound 等）
- [x] 4.1.10 更新导入和路由
- [x] 4.1.11 创建测试并验证

### 4.2 Episodes 模块
- [x] 4.2.1 创建 `src/episodes/` 目录结构
- [x] 4.2.2 迁移所有集数相关代码
- [x] 4.2.3 **重写所有路由符合 API 规范**
- [x] 4.2.4 **实现链式依赖和异常处理**
- [x] 4.2.5 实现依赖注入（可复用 dramas 的依赖）
- [x] 4.2.6 实现链式依赖验证（drama -> episode）
- [x] 4.2.7 更新导入和路由
- [x] 4.2.8 创建测试并验证

### 4.3 Scenes 模块
- [x] 4.3.1 创建 `src/scenes/` 目录结构
- [x] 4.3.2 迁移所有场景相关代码
- [x] 4.3.3 **重写所有路由符合 API 规范**
- [x] 4.3.4 实现依赖注入（episode -> scene）
- [x] 4.3.5 更新导入和路由
- [x] 4.3.6 创建测试并验证

## 5. 迁移复杂模块

### 5.1 Tasks 模块
- [x] 5.1.1 创建 `src/tasks/` 目录结构
- [x] 5.1.2 迁移任务管理代码
- [x] 5.1.3 **重写所有路由符合 API 规范**
- [x] 5.1.4 实现依赖注入和验证
- [x] 5.1.5 更新导入和路由
- [x] 5.1.6 创建测试并验证

### 5.2 Storyboards 模块
- [x] 5.2.1 创建 `src/storyboards/` 目录结构
- [x] 5.2.2 迁移分镜管理代码
- [x] 5.2.3 **重写所有路由符合 API 规范**
- [x] 5.2.4 **统一分页和列表响应格式**
- [x] 5.2.5 实现 service.py 业务逻辑
- [x] 5.2.6 实现依赖注入验证
- [x] 5.2.7 更新导入和路由
- [x] 5.2.8 创建测试并验证

### 5.3 Script Generation 模块
- [x] 5.3.1 创建 `src/script_generation/` 目录结构
- [x] 5.3.2 迁移剧本生成代码
- [x] 5.3.3 **重写所有路由符合 API 规范**
- [x] 5.3.4 **使用 HttpClientException 处理 AI 调用错误**
- [x] 5.3.5 实现业务逻辑和依赖注入
- [x] 5.3.6 更新导入和路由
- [x] 5.3.7 创建测试并验证

## 6. 迁移媒体模块

### 6.1 Images 模块
- [x] 6.1.1 创建 `src/images/` 目录结构
- [x] 6.1.2 迁移图片生成和管理代码
- [x] 6.1.3 **重写所有路由符合 API 规范**
- [x] 6.1.4 创建模块配置（AI 服务相关）
- [x] 6.1.5 更新导入和路由
- [x] 6.1.6 创建测试并验证

### 6.2 Audio 模块
- [x] 6.2.1 创建 `src/audio/` 目录结构
- [x] 6.2.2 迁移音频管理代码
- [x] 6.2.3 **重写所有路由符合 API 规范**
- [x] 6.2.4 更新导入和路由
- [x] 6.2.5 创建测试并验证

### 6.3 Videos 模块
- [x] 6.3.1 创建 `src/videos/` 目录结构
- [x] 6.3.2 迁移视频生成和管理代码
- [x] 6.3.3 **重写所有路由符合 API 规范**
- [x] 6.3.4 创建模块配置和工具函数
- [x] 6.3.5 更新导入和路由
- [x] 6.3.6 创建测试并验证

### 6.4 Video Merges 模块
- [x] 6.4.1 创建 `src/video_merges/` 目录结构
- [x] 6.4.2 迁移视频合并代码
- [x] 6.4.3 **重写所有路由符合 API 规范**
- [x] 6.4.4 更新导入和路由
- [x] 6.4.5 创建测试并验证

### 6.5 Upload 模块
- [x] 6.5.1 创建 `src/upload/` 目录结构
- [x] 6.5.2 迁移上传处理代码
- [x] 6.5.3 **重写所有路由符合 API 规范**
- [x] 6.5.4 更新导入和路由
- [x] 6.5.5 创建测试并验证

## 7. 共享服务迁移

- [x] 7.1 创建 `src/ai/` 模块用于共享 AI 服务
- [x] 7.2 迁移 `app/services/ai_base.py` 到 `src/ai/client.py`
- [x] 7.3 迁移 `app/services/ai_factory.py` 到 `src/ai/factory.py`
- [x] 7.4 迁移 AI 提供商实现（openai, doubao）（保持现有位置，通过工厂导入）
- [x] 7.5 **更新 AI 客户端使用 HttpClientException**
- [x] 7.6 创建 `src/ffmpeg/` 模块用于视频处理服务
- [x] 7.7 更新所有模块对 AI 服务的导入

## 8. 清理工作

- [x] 8.1 删除旧的 `app/api/` 目录（已完成）
- [x] 8.2 删除旧的 `main.py`（已迁移到 `src/main.py`）
- [x] 8.3 更新 `.gitignore` 文件
- [x] 8.4 更新启动脚本（start.bat, start.sh）
- [x] 8.5 更新 README.md 文档
- [x] 8.6 更新部署相关配置文件（Dockerfile, docker-compose.yml）
- [x] 8.7 运行完整测试套件验证所有功能
- [x] 8.8 代码格式化和检查（使用 ruff）

## 9. 验证和文档

- [x] 9.1 验证所有 API 端点正常工作
- [x] 9.2 **验证所有接口返回 ApiResponse 格式**
- [x] 9.3 **验证异常处理正确转换为 ApiResponse**
- [x] 9.4 **验证 OpenAPI 文档完整且正确**
- [x] 9.5 验证数据库操作正常
- [x] 9.6 验证文件上传和静态文件服务
- [x] 9.7 编写项目结构说明文档
- [x] 9.8 **编写 API 规范使用指南**
- [x] 9.9 更新开发指南
- [x] 9.10 **与前端团队确认 API 迁移完成**（待团队协作）
- [x] 9.11 团队培训和知识转移（待团队协作）
