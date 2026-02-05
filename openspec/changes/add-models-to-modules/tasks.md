# 任务清单

## 阶段一：基础设施

- [ ] 创建 `src/core/` 目录
- [ ] 复制 `src/config.py` → `src/core/config.py`
- [ ] 复制 `src/schemas.py` → `src/core/schemas.py`
- [ ] 修改 `src/database.py`，添加 Base 类定义
- [ ] 删除 `src/config.py`
- [ ] 删除 `src/schemas.py`

## 阶段二：创建模块模型

- [ ] 创建 `src/ai_configs/models.py`
- [ ] 创建 `src/assets/models.py`
- [ ] 创建 `src/audio/models.py`
- [ ] 创建 `src/character_library/models.py`
- [ ] 创建 `src/dramas/models.py`
- [ ] 创建 `src/episodes/models.py`
- [ ] 创建 `src/images/models.py`
- [ ] 创建 `src/scenes/models.py`
- [ ] 创建 `src/storyboards/models.py`
- [ ] 创建 `src/tasks/models.py`
- [ ] 创建 `src/videos/models.py`
- [ ] 创建 `src/video_merges/models.py`

## 阶段三：更新导入

- [ ] 更新 `src/main.py` 的导入
- [ ] 更新所有模块 router.py 的导入
- [ ] 更新所有模块 service.py 的导入
- [ ] 更新所有模块 dependencies.py 的导入
- [ ] 更新 `src/exception_handlers.py` 的导入

## 阶段四：验证

- [ ] 运行类型检查
- [ ] 验证数据库连接
- [ ] 测试 API 端点
