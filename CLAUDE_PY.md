# Python 后端项目完整分析 (CLAUDE_PY.md)

## 项目概述

**项目名称**: Drama Generation Backend (Python)
**框架**: FastAPI
**数据库**: PostgreSQL/MySQL + SQLAlchemy (Async)
**架构**: 分层架构 (Router -> Service -> Model)

## 项目结构

```
backend-python/
├── app/
│   ├── api/              # API 层
│   │   └── routes/       # 路由定义
│   ├── core/             # 核心配置
│   │   ├── config.py     # 配置管理
│   │   ├── database.py   # 数据库连接
│   │   ├── exceptions.py # 自定义异常
│   │   ├── exception_handlers.py # 异常处理器
│   │   ├── response.py   # 统一响应格式
│   │   └── security.py   # 安全相关
│   ├── models/           # 数据模型 (SQLAlchemy)
│   ├── schemas/          # Pydantic 模式 (请求/响应验证)
│   ├── services/         # 业务逻辑服务
│   └── utils/            # 工具函数
├── alembic/              # 数据库迁移
├── logs/                 # 日志文件
├── uploads/              # 上传文件存储
└── main.py               # 应用入口
```

---

## 1. API 路由完整列表

### 基础路径: `/api/v1`

#### 1.1 Dramas (剧本管理)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/dramas` | 获取剧本列表 (分页) |
| POST | `/dramas` | 创建剧本 |
| GET | `/dramas/{drama_id}` | 获取剧本详情 |
| PUT | `/dramas/{drama_id}` | 更新剧本 |
| DELETE | `/dramas/{drama_id}` | 删除剧本 |
| GET | `/dramas/{drama_id}/episodes` | 获取章节列表 |
| POST | `/dramas/{drama_id}/episodes` | 创建章节 |
| GET | `/dramas/{drama_id}/characters` | 获取角色列表 |
| POST | `/dramas/{drama_id}/characters` | 创建角色 |
| GET | `/dramas/stats` | 获取剧本统计 |
| PUT | `/dramas/{drama_id}/characters` | 批量保存角色 |
| PUT | `/dramas/{drama_id}/outline` | 保存大纲 |
| PUT | `/dramas/{drama_id}/episodes` | 批量保存章节 |
| PUT | `/dramas/{drama_id}/progress` | 保存进度 |

#### 1.2 Episodes (章节管理)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/episodes/{episode_id}` | 获取章节详情 |
| PUT | `/episodes/{episode_id}` | 更新章节 |
| DELETE | `/episodes/{episode_id}` | 删除章节 |
| POST | `/episodes/{episode_id}/finalize` | 完成章节 (视频合成) |
| GET | `/episodes/{episode_id}/download` | 下载章节视频 |
| POST | `/episodes/{episode_id}/storyboards` | 生成分镜 |
| GET | `/episodes/{episode_id}/storyboards` | 获取分镜列表 |

#### 1.3 AI Configs (AI 配置)
| 方法 | 路径 | 说明 |
|------|------|--------|
| GET | `/ai-configs` | 获取配置列表 |
| POST | `/ai-configs` | 创建配置 |
| POST | `/ai-configs/test` | 测试连接 |
| GET | `/ai-configs/{config_id}` | 获取配置详情 |
| PUT | `/ai-configs/{config_id}` | 更新配置 |
| DELETE | `/ai-configs/{config_id}` | 删除配置 |

#### 1.4 Generation (生成)
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/generation/characters` | 生成角色 |

#### 1.5 Character Library (角色库)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/character-library` | 获取角色库列表 |
| POST | `/character-library` | 创建角色库项 |
| GET | `/character-library/{item_id}` | 获取角色库项 |
| DELETE | `/character-library/{item_id}` | 删除角色库项 |

#### 1.6 Characters (角色)
| 方法 | 路径 | 说明 |
|------|------|------|
| PUT | `/characters/{id}` | 更新角色 |
| DELETE | `/characters/{id}` | 删除角色 |
| POST | `/characters/batch-generate-images` | 批量生成角色图片 |
| POST | `/characters/{id}/generate-image` | 生成角色图片 |
| PUT | `/characters/{id}/image` | 更新角色图片 |
| PUT | `/characters/{id}/image-from-library` | 应用角色库图片 |
| POST | `/characters/{id}/add-to-library` | 添加到角色库 |

#### 1.7 Upload (上传)
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/upload/image` | 上传图片 |
| POST | `/upload/video` | 上传视频 |
| POST | `/upload/audio` | 上传音频 |

#### 1.8 Tasks (任务)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/tasks/{task_id}` | 获取任务状态 |
| GET | `/tasks` | 获取资源任务列表 |

#### 1.9 Scenes (场景)
| 方法 | 路径 | 说明 |
|------|------|------|
| PUT | `/scenes/{scene_id}` | 更新场景 |
| PUT | `/scenes/{scene_id}/prompt` | 更新场景提示词 |
| DELETE | `/scenes/{scene_id}` | 删除场景 |
| POST | `/scenes/generate-image` | 生成场景图片 |

#### 1.10 Images (图片生成)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/images` | 获取图片生成列表 |
| POST | `/images` | 生成图片 |
| GET | `/images/{gen_id}` | 获取图片生成详情 |
| DELETE | `/images/{gen_id}` | 删除图片生成记录 |

#### 1.11 Videos (视频生成)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/videos` | 获取视频生成列表 |
| POST | `/videos` | 生成视频 |
| GET | `/videos/{gen_id}` | 获取视频生成详情 |
| DELETE | `/videos/{gen_id}` | 删除视频生成记录 |

#### 1.12 Video Merges (视频合并)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/video-merges` | 获取视频合并列表 |
| POST | `/video-merges` | 合并视频 |
| GET | `/video-merges/{merge_id}` | 获取视频合并详情 |
| DELETE | `/video-merges/{merge_id}` | 删除视频合并记录 |

#### 1.13 Assets (素材)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/assets` | 获取素材列表 |
| POST | `/assets` | 创建素材 |
| GET | `/assets/{asset_id}` | 获取素材详情 |
| PUT | `/assets/{asset_id}` | 更新素材 |
| DELETE | `/assets/{asset_id}` | 删除素材 |
| POST | `/assets/import/image/{image_gen_id}` | 从图片生成导入 |
| POST | `/assets/import/video/{video_gen_id}` | 从视频生成导入 |

#### 1.14 Storyboards (分镜)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/storyboards/{storyboard_id}` | 获取分镜详情 |
| PUT | `/storyboards/{storyboard_id}` | 更新分镜 |
| DELETE | `/storyboards/{storyboard_id}` | 删除分镜 |
| POST | `/storyboards/{storyboard_id}/frame-prompt` | 生成帧提示词 |
| GET | `/storyboards/{storyboard_id}/frame-prompts` | 获取帧提示词列表 |

#### 1.15 Audio (音频)
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/audio/extract` | 提取音频 |
| POST | `/audio/extract/batch` | 批量提取音频 |

#### 1.16 Settings (设置)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/settings/language` | 获取语言设置 |
| PUT | `/settings/language` | 更新语言设置 |

---

## 2. 数据模型

### 2.1 Drama (剧本)
```python
class Drama(Base):
    __tablename__ = "dramas"

    id: int (PK, AutoIncrement)
    title: str (200)
    description: str (Text, Optional)
    genre: str (50, Optional)
    style: str (50, default="realistic")
    total_episodes: int (default=1)
    total_duration: int (default=0)
    status: str (20, default="draft")
    thumbnail: str (500, Optional)
    tags: JSON (Optional)
    metadata: JSON (Optional)
    created_at: DateTime
    updated_at: DateTime
    deleted_at: DateTime (Optional, Soft delete)

    # 关联
    episodes: List[Episode]
    characters: List[Character]
    scenes: List[Scene]
```

### 2.2 Episode (章节)
```python
class Episode(Base):
    __tablename__ = "episodes"

    id: int (PK, AutoIncrement)
    drama_id: int (FK -> dramas.id)
    episode_number: int
    title: str (200)
    script_content: str (Text, Optional)
    description: str (Text, Optional)
    duration: int (default=0)
    status: str (20, default="draft")
    video_url: str (500, Optional)
    thumbnail: str (500, Optional)
    created_at: DateTime
    updated_at: DateTime
    deleted_at: DateTime (Optional, Soft delete)

    # 关联
    drama: Drama
    characters: List[Character] (Many-to-Many)
    storyboards: List[Storyboard]
    scenes: List[Scene]
```

### 2.3 Character (角色)
```python
class Character(Base):
    __tablename__ = "characters"

    id: int (PK, AutoIncrement)
    drama_id: int (FK -> dramas.id)
    name: str (100)
    role: str (50, Optional)
    description: str (Text, Optional)
    appearance: str (Text, Optional)
    personality: str (Text, Optional)
    voice_style: str (200, Optional)
    image_url: str (500, Optional)
    reference_images: JSON (Optional)
    seed_value: str (100, Optional)
    sort_order: int (default=0)
    created_at: DateTime
    updated_at: DateTime
    deleted_at: DateTime (Optional, Soft delete)

    # 关联
    drama: Drama
    episodes: List[Episode] (Many-to-Many)
```

### 2.4 Storyboard (分镜)
```python
class Storyboard(Base):
    __tablename__ = "storyboards"

    id: int (PK, AutoIncrement)
    drama_id: int (FK -> dramas.id)
    episode_id: int (FK -> episodes.id)
    scene_id: int (FK -> scenes.id, Optional)
    storyboard_number: int
    title: str (255, Optional)
    location: str (255, Optional)
    time: str (255, Optional)
    shot_type: str (100, Optional)
    angle: str (100, Optional)
    movement: str (100, Optional)
    action: str (Text, Optional)
    result: str (Text, Optional)
    atmosphere: str (Text, Optional)
    image_prompt: str (Text, Optional)
    video_prompt: str (Text, Optional)
    bgm_prompt: str (Text, Optional)
    sound_effect: str (255, Optional)
    dialogue: str (Text, Optional)
    description: str (Text, Optional)
    duration: int (default=5)
    composed_image: str (Text, Optional)
    video_url: str (Text, Optional)
    status: str (20, default="pending")
    created_at: DateTime
    updated_at: DateTime
    deleted_at: DateTime (Optional, Soft delete)

    # 关联
    drama: Drama
    episode: Episode
    scene: Scene
```

### 2.5 Scene (场景)
```python
class Scene(Base):
    __tablename__ = "scenes"

    id: int (PK, AutoIncrement)
    drama_id: int (FK -> dramas.id)
    episode_id: int (FK -> episodes.id, Optional)
    location: str (200)
    time: str (100)
    prompt: str (Text)
    storyboard_count: int (default=1)
    image_url: str (500, Optional)
    status: str (20, default="pending")
    created_at: DateTime
    updated_at: DateTime
    deleted_at: DateTime (Optional, Soft delete)

    # 关联
    drama: Drama
    episode: Episode
```

### 2.6 ImageGeneration (图片生成记录)
```python
class ImageGeneration(Base):
    __tablename__ = "image_generations"

    id: int (PK, AutoIncrement)
    storyboard_id: int (FK -> storyboards.id, Optional)
    drama_id: int (FK -> dramas.id)
    scene_id: int (FK -> scenes.id, Optional)
    character_id: int (FK -> characters.id, Optional)
    image_type: str (20, default="storyboard")
    frame_type: str (20, Optional)
    provider: str (50)
    prompt: str (Text)
    negative_prompt: str (Text, Optional)
    model: str (100, Optional)
    size: str (20, Optional)
    quality: str (20, Optional)
    style: str (50, Optional)
    steps: int (Optional)
    cfg_scale: float (Optional)
    seed: float (Optional)
    image_url: str (Text, Optional)
    minio_url: str (Text, Optional)
    local_path: str (Text, Optional)
    status: str (20, default="pending")
    task_id: str (200, Optional)
    error_msg: str (Text, Optional)
    width: int (Optional)
    height: int (Optional)
    reference_images: JSON (Optional)
    created_at: DateTime
    updated_at: DateTime
    completed_at: DateTime (Optional)

    # 关联
    storyboard: Storyboard
    drama: Drama
    scene: Scene
    character: Character
    assets: List[Asset]
```

**状态枚举**:
- `pending`: 等待处理
- `processing`: 处理中
- `completed`: 完成
- `failed`: 失败

**图片类型**:
- `character`: 角色图片
- `scene`: 场景图片
- `storyboard`: 分镜图片

### 2.7 VideoGeneration (视频生成记录)
```python
class VideoGeneration(Base):
    __tablename__ = "video_generations"

    id: int (PK, AutoIncrement)
    created_at: DateTime
    updated_at: DateTime

    storyboard_id: int (FK -> storyboards.id, Optional)
    drama_id: int (FK -> dramas.id)
    image_gen_id: int (FK -> image_generations.id, Optional)

    provider: str (50)
    prompt: str (Text)
    model: str (100, Optional)

    reference_mode: str (20, Optional)  # single, first_last, multiple, none

    image_url: str (1000, Optional)
    first_frame_url: str (1000, Optional)
    last_frame_url: str (1000, Optional)
    reference_image_urls: str (Text, Optional)  # JSON array

    duration: int (Optional)
    fps: int (Optional)
    resolution: str (50, Optional)
    aspect_ratio: str (20, Optional)
    style: str (100, Optional)
    motion_level: int (Optional)
    camera_motion: str (100, Optional)
    seed: float (Optional)

    video_url: str (1000, Optional)
    minio_url: str (1000, Optional)
    local_path: str (500, Optional)

    status: str (20, default="pending")
    task_id: str (200, Optional)
    error_msg: str (Text, Optional)
    completed_at: DateTime (Optional)

    width: int (Optional)
    height: int (Optional)

    # 关联
    storyboard: Storyboard
    drama: Drama
    image_gen: ImageGeneration
```

**视频状态**: `pending`, `processing`, `completed`, `failed`

### 2.8 VideoMerge (视频合并记录)
```python
class VideoMerge(Base):
    __tablename__ = "video_merges"

    id: int (PK, AutoIncrement)
    episode_id: int (FK -> episodes.id)
    drama_id: int (FK -> dramas.id)
    title: str (200, Optional)
    provider: str (50)
    model: str (100, Optional)
    status: str (20, default="pending")
    scenes: JSON  # Array of scene clips
    merged_url: str (500, Optional)
    duration: int (Optional)
    task_id: str (100, Optional)
    error_msg: str (Text, Optional)
    created_at: DateTime
    completed_at: DateTime (Optional)

    # 关联
    episode: Episode
    drama: Drama
```

### 2.9 AsyncTask (异步任务)
```python
class AsyncTask(Base):
    __tablename__ = "async_tasks"

    id: str (36, PK)  # UUID
    type: str (50)  # storyboard_generation, etc.
    status: str (20)  # pending, processing, completed, failed
    progress: int (0-100, default=0)
    message: str (500, Optional)
    error: str (Text, Optional)
    result: str (Text, Optional)  # JSON string
    resource_id: str (36)
    created_at: DateTime
    updated_at: DateTime
    completed_at: DateTime (Optional)
```

### 2.10 Asset (素材)
```python
class Asset(Base):
    __tablename__ = "assets"

    id: int (PK, AutoIncrement)
    created_at: DateTime
    updated_at: DateTime

    drama_id: int (FK -> dramas.id, Optional)
    episode_id: int (FK -> episodes.id, Optional)
    storyboard_id: int (FK -> storyboards.id, Optional)
    storyboard_num: int (Optional)

    name: str (200)
    description: str (Text, Optional)
    type: str (20)  # image, video, audio
    category: str (50, Optional)
    url: str (1000)
    thumbnail_url: str (1000, Optional)
    local_path: str (500, Optional)

    file_size: float (Optional)
    mime_type: str (100, Optional)
    width: int (Optional)
    height: int (Optional)
    duration: int (Optional)
    format: str (50, Optional)

    image_gen_id: int (FK -> image_generations.id, Optional)
    video_gen_id: int (FK -> video_generations.id, Optional)

    is_favorite: bool (default=False)
    view_count: int (default=0)

    # 关联
    drama: Drama
    image_gen: ImageGeneration
    video_gen: VideoGeneration
```

**素材类型**: `image`, `video`, `audio`

### 2.11 CharacterLibrary (角色库)
```python
class CharacterLibrary(Base):
    __tablename__ = "character_libraries"

    id: int (PK, AutoIncrement)
    name: str (100)
    category: str (50, Optional)
    image_url: str (500)
    description: str (Text, Optional)
    tags: str (500, Optional)
    source_type: str (20, default="generated")
    created_at: DateTime
    updated_at: DateTime
```

---

## 3. 响应格式

### 3.1 统一响应结构
```python
class APIResponse:
    @staticmethod
    def success(data=None, message=None) -> dict:
        return {
            "success": True,
            "data": data,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    @staticmethod
    def error(code: str, message: str, details=None) -> dict:
        return {
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
```

### 3.2 分页响应
```python
@staticmethod
def success_with_pagination(items, total, page, page_size) -> dict:
    total_pages = (total + page_size - 1) // page_size
    return {
        "success": True,
        "data": {
            "items": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages
            }
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
```

### 3.3 响应函数
- `success(data, message)` - 成功响应 (200)
- `created(data)` - 创建成功响应 (201)
- `success_with_pagination(items, total, page, page_size)` - 分页响应
- `error(code, message, details)` - 错误响应
- `bad_request(message)` - 错误请求 (400)
- `unauthorized(message)` - 未授权 (401)
- `forbidden(message)` - 禁止访问 (403)
- `not_found(message)` - 未找到 (404)
- `internal_error(message)` - 内部错误 (500)

---

## 4. 中间件

### 4.1 CORS 中间件
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4.2 异常处理中间件
```python
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
```

---

## 5. 服务层 (app/services/)

| 服务 | 职责 |
|------|------|
| `ImageGenerationService` | 图片生成服务 |
| `VideoGenerationService` | 视频生成服务 |
| `VideoMergeService` | 视频合并服务 |
| `StoryboardService` | 分镜生成服务 |
| `CharacterLibraryService` | 角色库服务 |
| `TaskService` | 异步任务管理 |
| `FFmpegService` | FFmpeg 音频提取和视频合并 |
| `ScriptGenerationService` | 脚本生成服务 |
| `ResourceTransferService` | 资源传输服务 |
| `FramePromptService` | 帧提示词生成服务 |

---

## 6. AI 客户端 (app/services/)

### 6.1 AI 基础接口
- `ai_base.py` - AI 基础接口定义
  - `ImageGenerationRequest`
  - `ImageGenerationResponse`
  - `AIClient` (ABC)

### 6.2 AI 提供商实现
- `ai_openai.py` - OpenAI 客户端
- `ai_doubao.py` - 豆包客户端
- `ai_factory.py` - AI 客户端工厂

---

## 7. 关键特性

1. **统一响应格式**: 所有 API 返回统一的 JSON 结构 (与 Go 一致)
2. **异步支持**: 使用 Async SQLAlchemy 和异步路由
3. **异常处理**: 全局异常处理器，统一错误格式
4. **FFmpeg 集成**: 音频提取和视频合并服务
5. **分页支持**: 列表接口支持分页
6. **软删除**: 使用 `deleted_at` 字段
7. **中间件**: CORS、全局异常处理
8. **静态文件服务**: 本地存储

---

## 8. 配置项

主要配置在 `app/core/config.py`:
- `APP_NAME`: 应用名称
- `APP_VERSION`: 应用版本
- `HOST`: 服务器主机
- `PORT`: 服务器端口
- `DATABASE_URL`: 数据库连接
- `LOCAL_STORAGE_PATH`: 本地存储路径
- `BASE_URL`: Base URL
- `LOG_PATH`: 日志路径
- `CORS_ORIGINS`: CORS 允许的源

---

## 9. 依赖

主要 Python 依赖:
- `fastapi` - Web 框架
- `uvicorn` - ASGI 服务器
- `sqlalchemy` - ORM (Async)
- `alembic` - 数据库迁移
- `pydantic` - 数据验证
- `python-multipart` - 文件上传支持

---

## 10. 端口总结

**HTTP 端口**: 默认 8000
**静态文件**: `/static`
**API 前缀**: `/api/v1`
**健康检查**: `/health`
**API 文档**: `/docs` (Swagger)

---

## 11. 与 Go 后端的主要差异

### 已同步
- ✅ 统一响应格式 (`success`, `data`, `error`, `timestamp`)
- ✅ 异常处理机制
- ✅ 数据模型结构
- ✅ 路由结构
- ✅ FFmpeg 服务

### 待确认
- ❓ 部分路由的响应格式是否完全一致
- ❓ AI 客户端的完整实现
- ❓ 异步任务处理的完整实现
