# 任务清单

## 阶段一：基础设施

- [x] 创建 `src/core/` 目录
- [x] 复制 `src/config.py` → `src/core/config.py`
- [x] 复制 `src/schemas.py` → `src/core/schemas.py`
- [x] 修改 `src/database.py`，添加 Base 类定义
- [x] 删除 `src/config.py`
- [x] 删除 `src/schemas.py`

## 阶段二：创建模块模型

- [x] 创建 `src/ai_configs/models.py`
- [x] 创建 `src/assets/models.py`
- [x] 创建 `src/audio/models.py` (无需持久化存储)
- [x] 创建 `src/character_library/models.py`
- [x] 创建 `src/dramas/models.py`
- [x] 创建 `src/episodes/models.py`
- [x] 创建 `src/images/models.py`
- [x] 创建 `src/scenes/models.py`
- [x] 创建 `src/storyboards/models.py`
- [x] 创建 `src/tasks/models.py`
- [x] 创建 `src/videos/models.py`
- [x] 创建 `src/video_merges/models.py`

## 阶段三：更新导入

- [x] 更新 `src/main.py` 的导入
- [x] 更新所有模块 router.py 的导入
- [x] 更新所有模块 service.py 的导入
- [x] 更新所有模块 dependencies.py 的导入
- [x] 更新 `src/exception_handlers.py` 的导入

## 阶段四：验证

- [x] 运行类型检查
- [x] 验证数据库连接
- [x] 测试 API 端点
