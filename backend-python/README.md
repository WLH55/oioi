# 火豹剧片后端 - Python版本

这是火豹剧片AI短剧生成平台的Python重构版本，使用FastAPI框架实现。

## 技术栈

- **Web框架**: FastAPI 0.109.0
- **ORM**: SQLAlchemy 2.0 (异步)
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **验证**: Pydantic v2
- **任务处理**: FastAPI BackgroundTasks
- **日志**: Loguru

## 项目结构

```
backend-python/
├── app/
│   ├── api/                    # API路由
│   │   ├── routes/            # 路由实现
│   │   └── dependencies/      # 依赖注入
│   ├── models/                # SQLAlchemy数据库模型
│   ├── schemas/               # Pydantic数据验证模型
│   ├── services/              # 业务逻辑服务层
│   ├── core/                  # 核心配置
│   │   ├── config.py         # 配置管理
│   │   ├── database.py       # 数据库连接
│   │   └── security.py       # 安全相关
│   └── utils/                 # 工具函数
├── uploads/                   # 上传文件目录
├── data/                      # 数据库文件
├── logs/                      # 日志文件
├── main.py                    # 应用入口
├── requirements.txt           # Python依赖
└── .env.example              # 环境变量示例
```

## 快速开始

### 1. 环境要求

- Python 3.10+
- pip

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，修改必要的配置
# 如：数据库路径、API密钥等
```

### 4. 运行应用

```bash
# 开发模式（带热重载）
python main.py

# 或者使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

应用将在 `http://localhost:8000` 启动。

### 5. 访问API文档

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API端点

### 健康检查
- `GET /health` - 服务健康检查

### 剧片管理
- `GET /api/v1/dramas` - 获取剧片列表
- `POST /api/v1/dramas` - 创建剧片
- `GET /api/v1/dramas/{id}` - 获取剧片详情
- `PUT /api/v1/dramas/{id}` - 更新剧片
- `DELETE /api/v1/dramas/{id}` - 删除剧片
- `GET /api/v1/dramas/{id}/episodes` - 获取章节列表
- `POST /api/v1/dramas/{id}/episodes` - 创建章节
- `GET /api/v1/dramas/{id}/characters` - 获取角色列表
- `POST /api/v1/dramas/{id}/characters` - 创建角色

### AI配置管理
- `GET /api/v1/ai-configs` - 获取AI配置列表
- `POST /api/v1/ai-configs` - 创建AI配置
- `GET /api/v1/ai-configs/{id}` - 获取AI配置详情
- `PUT /api/v1/ai-configs/{id}` - 更新AI配置
- `DELETE /api/v1/ai-configs/{id}` - 删除AI配置
- `POST /api/v1/ai-configs/test` - 测试AI连接

### 图片生成
- `GET /api/v1/images` - 获取图片生成列表
- `POST /api/v1/images` - 生成图片
- `GET /api/v1/images/{id}` - 获取图片生成详情
- `DELETE /api/v1/images/{id}` - 删除图片生成

### 视频生成
- `GET /api/v1/videos` - 获取视频生成列表
- `POST /api/v1/videos` - 生成视频
- `GET /api/v1/videos/{id}` - 获取视频生成详情
- `DELETE /api/v1/videos/{id}` - 删除视频生成

### 任务管理
- `GET /api/v1/tasks/{task_id}` - 获取任务状态
- `GET /api/v1/tasks` - 获取任务列表

## 数据库模型

### 核心模型

1. **Drama** - 剧片
   - 包含标题、描述、类型、风格等信息
   - 关联章节、角色、场景

2. **Episode** - 章节
   - 章节编号、标题、剧本内容
   - 关联分镜、场景

3. **Character** - 角色
   - 角色名称、外貌、性格
   - 角色图片、种子值

4. **Scene** - 场景
   - 场景地点、时间、提示词
   - 场景图片

5. **Storyboard** - 分镜
   - 分镜编号、镜头类型、运镜
   - 图片/视频提示词、对话

6. **ImageGeneration** - 图片生成记录
   - 提供商、提示词、参数
   - 生成状态、任务ID

7. **VideoGeneration** - 视频生成记录
   - 参考模式、视频参数
   - 生成状态、视频URL

8. **AIServiceConfig** - AI服务配置
   - 服务类型、提供商、模型
   - API密钥、优先级

9. **AsyncTask** - 异步任务
   - 任务类型、状态、进度
   - 错误信息、结果数据

10. **Asset** - 资源
    - 资源类型（图片/视频/音频）
    - 文件信息、元数据

## 开发指南

### 添加新的API路由

1. 在 `app/api/routes/` 创建新的路由文件
2. 在 `app/schemas/` 创建请求/响应模型
3. 在 `app/models/` 创建数据库模型（如果需要）
4. 在 `app/services/` 创建业务逻辑（如果需要）
5. 在 `main.py` 中注册路由

### 数据库迁移

当前使用自动创建表的方式。对于生产环境，建议使用 Alembic 进行数据库迁移：

```bash
# 初始化 Alembic
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "description"

# 执行迁移
alembic upgrade head
```

### 异步任务处理

使用 FastAPI 的 BackgroundTasks 处理简单异步任务：

```python
from fastapi import BackgroundTasks

async def process_task(task_id: int):
    # 后台任务逻辑
    pass

@router.post("/tasks")
async def create_task(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_task, task_id=123)
    return {"status": "pending"}
```

对于复杂的任务队列需求，可以集成 Celery：

```bash
pip install celery redis
```

## 环境变量配置

参考 `.env.example` 文件配置以下变量：

```env
# 应用配置
APP_NAME=huobao-drama
APP_VERSION=1.0.0
DEBUG=True

# 服务器配置
HOST=0.0.0.0
PORT=8000

# CORS配置
CORS_ORIGINS=["http://localhost:5173"]

# 数据库配置
DATABASE_TYPE=sqlite
SQLITE_PATH=./data/drama.db

# 存储配置
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./uploads

# AI配置
DEFAULT_AI_PROVIDER=openai

# 日志配置
LOG_LEVEL=INFO
LOG_PATH=./logs
```

## 测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio httpx

# 运行测试
pytest

# 运行测试并查看覆盖率
pytest --cov=app --cov-report=html
```

## 部署

### Docker部署

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

构建和运行：

```bash
docker build -t huobao-drama-backend .
docker run -p 8000:8000 huobao-drama-backend
```

### 生产环境建议

1. 使用 PostgreSQL 替代 SQLite
2. 配置 Nginx 作为反向代理
3. 使用 Gunicorn + Uvicorn workers
4. 启用 HTTPS
5. 配置日志收集和监控
6. 使用 Redis 作为缓存和任务队列

## 与Go版本的对比

### 相同功能

✅ 完整的API接口
✅ 数据库模型结构
✅ 业务逻辑功能
✅ AI集成能力

### 优势

- 🚀 更容易的异步编程（Python asyncio vs Go goroutines）
- 📚 更丰富的AI/ML库支持
- 🔧 更容易的定制和修改
- 📊 自动生成的API文档

### 注意事项

- ⚠️ 性能：Go版本在高并发场景下性能更优
- ⚠️ 部署：Python版本需要更多资源
- ⚠️ 类型安全：Go有更强的类型系统

## 未来改进

- [ ] 完善所有API路由实现
- [ ] 添加完整的业务服务层
- [ ] 实现AI集成服务（OpenAI、豆包等）
- [ ] 添加文件上传和处理
- [ ] 实现视频合并功能
- [ ] 添加WebSocket支持（实时进度）
- [ ] 完善错误处理和日志
- [ ] 添加单元测试和集成测试
- [ ] 实现缓存机制
- [ ] 添加API限流和安全认证

## 许可证

[根据原项目许可证]

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

[项目联系方式]
