# 提案：为各模块添加 SQLAlchemy 模型

## 问题

当前代码存在以下问题：
1. `app/` 目录已不存在，但代码仍在引用它
2. 没有在各业务模块中定义 SQLAlchemy 模型类
3. 数据库模型分散或缺失

## 目标

1. 在 `src/{模块}/` 目录下创建各自的 `models.py` 文件
2. 每个模块定义自己的 SQLAlchemy 模型
3. 保留 `src/database.py` 用于 Base 元类和异步引擎配置
4. 更新所有导入路径

## 范围

### 需要添加模型的模块

| 模块 | 模型 |
|------|------|
| ai_configs | AIConfig |
| assets | Asset |
| audio | Audio |
| character_library | Character |
| dramas | Drama |
| episodes | Episode |
| images | ImageGeneration |
| scenes | Scene |
| storyboards | Storyboard |
| tasks | Task |
| videos | VideoGeneration |
| video_merges | VideoMerge |

### 不需要添加模型的模块

- health - 仅健康检查
- settings - 配置较少，可使用简单模型
- upload - 使用临时模型

## 实现步骤

1. 创建 `src/core/` 目录，迁移配置和 schemas
2. 修改 `src/database.py`，定义 Base 和异步引擎
3. 为每个业务模块创建 `models.py`
4. 更新模块的 `__init__.py` 导出模型
5. 更新所有导入路径

## 风险

- 需要确保模型之间的外键关系正确
- 迁移期间应用可能无法正常工作
