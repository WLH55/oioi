# Go 后端项目完整分析 (CLAUDE_GO.md)

## 项目概述

**项目名称**: Drama Generation Backend (Go)
**框架**: Gin (Go Web Framework)
**数据库**: MySQL/PostgreSQL + GORM
**架构**: 分层架构 (Handler -> Service -> Model)

## 项目结构

```
backend-go/
├── api/                    # API 层
│   ├── handlers/          # 请求处理器 (Controller 层)
│   ├── middlewares/       # 中间件
│   └── routes/            # 路由配置
├── application/           # 应用服务层
│   └── services/          # 业务逻辑
├── domain/                # 领域层
│   └── models/            # 数据模型
├── infrastructure/        # 基础设施层
│   ├── database/          # 数据库连接
│   ├── external/          # 外部服务集成
│   ├── scheduler/         # 定时任务
│   └── storage/           # 文件存储
├── migrations/            # 数据库迁移
├── pkg/                   # 工具包
│   ├── ai/               # AI 服务客户端
│   ├── config/           # 配置管理
│   ├── image/            # 图片生成客户端
│   ├── logger/           # 日志工具
│   ├── response/         # 统一响应格式
│   ├── utils/            # 工具函数
│   └── video/            # 视频生成客户端
└── configs/              # 配置文件
```

---

## 1. API 路由完整列表

### 基础路径: `/api/v1`

#### 1.1 Dramas (剧本管理)
| 方法 | 路径 | 处理器 | 说明 |
|------|------|--------|------|
| GET | `/dramas` | `ListDramas` | 获取剧本列表 (分页) |
| POST | `/dramas` | `CreateDrama` | 创建剧本 |
| GET | `/dramas/stats` | `GetDramaStats` | 获取剧本统计 |
| GET | `/dramas/:id/characters` | `GetCharacters` | 获取角色列表 |
| PUT | `/dramas/:id/characters` | `SaveCharacters` | 批量保存角色 |
| PUT | `/dramas/:id/outline` | `SaveOutline` | 保存大纲 |
| PUT | `/dramas/:id/episodes` | `SaveEpisodes` | 批量保存章节 |
| PUT | `/dramas/:id/progress` | `SaveProgress` | 保存进度 |
| GET | `/dramas/:id` | `GetDrama` | 获取剧本详情 |
| PUT | `/dramas/:id` | `UpdateDrama` | 更新剧本 |
| DELETE | `/dramas/:id` | `DeleteDrama` | 删除剧本 |

#### 1.2 Episodes (章节管理)
| 方法 | 路径 | 处理器 | 说明 |
|------|------|--------|------|
| POST | `/episodes/:episode_id/storyboards` | `GenerateStoryboard` | 生成分镜 |
| GET | `/episodes/:episode_id/storyboards` | `GetStoryboardsForEpisode` | 获取分镜列表 |
| POST | `/episodes/:episode_id/finalize` | `FinalizeEpisode` | 完成章节 (视频合成) |
| GET | `/episodes/:episode_id/download` | `DownloadEpisodeVideo` | 下载章节视频 |

#### 1.3 AI Configs (AI 配置)
| 方法 | 路径 | 处理器 | 说明 |
|------|------|--------|------|
| GET | `/ai-configs` | `ListConfigs` | 获取配置列表 |
| POST | `/ai-configs` | `CreateConfig` | 创建配置 |
| POST | `/ai-configs/test` | `TestConnection` | 测试连接 |
| GET | `/ai-configs/:id` | `GetConfig` | 获取配置详情 |
| PUT | `/ai-configs/:id` | `UpdateConfig` | 更新配置 |
| DELETE | `/ai-configs/:id` | `DeleteConfig` | 删除配置 |

#### 1.4 Generation (生成)
| 方法 | 路径 | 处理器 | 说明 |
|------|------|--------|------|
| POST | `/generation/characters` | `GenerateCharacters` | 生成角色 |

#### 1.5 Character Library (角色库)
| 方法 | 路径 | 处理器 | 说明 |
|------|------|--------|------|
| GET | `/character-library` | `ListLibraryItems` | 获取角色库列表 |
| POST | `/character-library` | `CreateLibraryItem` | 创建角色库项 |
| GET | `/character-library/:id` | `GetLibraryItem` | 获取角色库项 |
| DELETE | `/character-library/:id` | `DeleteLibraryItem` | 删除角色库项 |

#### 1.6 Characters (角色)
| 方法 | 路径 | 处理器 | 说明 |
|------|------|--------|------|
| PUT | `/characters/:id` | `UpdateCharacter` | 更新角色 |
| DELETE | `/characters/:id` | `DeleteCharacter` | 删除角色 |
| POST | `/characters/batch-generate-images` | `BatchGenerateCharacterImages` | 批量生成角色图片 |
| POST | `/characters/:id/generate-image` | `GenerateCharacterImage` | 生成角色图片 |
| POST | `/characters/:id/upload-image` | `UploadCharacterImage` | 上传角色图片 |
| PUT | `/characters/:id/image` | `UploadCharacterImage` | 更新角色图片 |
| PUT | `/characters/:id/image-from-library` | `ApplyLibraryItemToCharacter` | 应用角色库图片 |
| POST | `/characters/:id/add-to-library` | `AddCharacterToLibrary` | 添加到角色库 |

#### 1.7 Upload (上传)
| 方法 | 路径 | 处理器 | 说明 |
|------|------|--------|------|
| POST | `/upload/image` | `UploadImage` | 上传图片 |

#### 1.8 Tasks (任务)
| 方法 | 路径 | 处理器 | 说明 |
|------|------|--------|------|
| GET | `/tasks/:task_id` | `GetTaskStatus` | 获取任务状态 |
| GET | `/tasks` | `GetResourceTasks` | 获取资源任务列表 |

#### 1.9 Scenes (场景)
| 方法 | 路径 | 处理器 | 说明 |
|------|------|--------|------|
| PUT | `/scenes/:scene_id` | `UpdateScene` | 更新场景 |
| PUT | `/scenes/:scene_id/prompt` | `UpdateScenePrompt` | 更新场景提示词 |
| DELETE | `/scenes/:scene_id` | `DeleteScene` | 删除场景 |
| POST | `/scenes/generate-image` | `GenerateSceneImage` | 生成场景图片 |

#### 1.10 Images (图片生成)
| 方法 | 路径 | 处理器 | 说明 |
|------|------|--------|------|
| GET | `/images` | `ListImageGenerations` | 获取图片生成列表 |
| POST | `/images` | `GenerateImage` | 生成图片 |
| GET | `/images/:id` | `GetImageGeneration` | 获取图片生成详情 |
| DELETE | `/images/:id` | `DeleteImageGeneration` | 删除图片生成记录 |
| POST | `/images/scene/:scene_id` | `GenerateImagesForScene` | 为场景生成图片 |
| GET | `/images/episode/:episode_id/backgrounds` | `GetBackgroundsForEpisode` | 获取章节背景图 |
| POST | `/images/episode/:episode_id/backgrounds/extract` | `ExtractBackgroundsForEpisode` | 提取章节背景图 |
| POST | `/images/episode/:episode_id/batch` | `BatchGenerateForEpisode` | 批量生成章节图片 |

#### 1.11 Videos (视频生成)
| 方法 | 路径 | 处理器 | 说明 |
|------|------|--------|------|
| GET | `/videos` | `ListVideoGenerations` | 获取视频生成列表 |
| POST | `/videos` | `GenerateVideo` | 生成视频 |
| GET | `/videos/:id` | `GetVideoGeneration` | 获取视频生成详情 |
| DELETE | `/videos/:id` | `DeleteVideoGeneration` | 删除视频生成记录 |
| POST | `/videos/image/:image_gen_id` | `GenerateVideoFromImage` | 从图片生成视频 |
| POST | `/videos/episode/:episode_id/batch` | `BatchGenerateForEpisode` | 批量生成章节视频 |

#### 1.12 Video Merges (视频合并)
| 方法 | 路径 | 处理器 | 说明 |
|------|------|--------|------|
| GET | `/video-merges` | `ListMerges` | 获取视频合并列表 |
| POST | `/video-merges` | `MergeVideos` | 合并视频 |
| GET | `/video-merges/:merge_id` | `GetMerge` | 获取视频合并详情 |
| DELETE | `/video-merges/:merge_id` | `DeleteMerge` | 删除视频合并记录 |

#### 1.13 Assets (素材)
| 方法 | 路径 | 处理器 | 说明 |
|------|------|--------|------|
| GET | `/assets` | `ListAssets` | 获取素材列表 |
| POST | `/assets` | `CreateAsset` | 创建素材 |
| GET | `/assets/:id` | `GetAsset` | 获取素材详情 |
| PUT | `/assets/:id` | `UpdateAsset` | 更新素材 |
| DELETE | `/assets/:id` | `DeleteAsset` | 删除素材 |
| POST | `/assets/import/image/:image_gen_id` | `ImportFromImageGen` | 从图片生成导入 |
| POST | `/assets/import/video/:video_gen_id` | `ImportFromVideoGen` | 从视频生成导入 |

#### 1.14 Storyboards (分镜)
| 方法 | 路径 | 处理器 | 说明 |
|------|------|--------|------|
| PUT | `/storyboards/:id` | `UpdateStoryboard` | 更新分镜 |
| POST | `/storyboards/:id/frame-prompt` | `GenerateFramePrompt` | 生成帧提示词 |
| GET | `/storyboards/:id/frame-prompts` | `GetStoryboardFramePrompts` | 获取帧提示词列表 |

#### 1.15 Audio (音频)
| 方法 | 路径 | 处理器 | 说明 |
|------|------|--------|------|
| POST | `/audio/extract` | `ExtractAudio` | 提取音频 |
| POST | `/audio/extract/batch` | `BatchExtractAudio` | 批量提取音频 |

#### 1.16 Settings (设置)
| 方法 | 路径 | 处理器 | 说明 |
|------|------|--------|------|
| GET | `/settings/language` | `GetLanguage` | 获取语言设置 |
| PUT | `/settings/language` | `UpdateLanguage` | 更新语言设置 |

---

## 2. 数据模型

### 2.1 Drama (剧本)
```go
type Drama struct {
    ID            uint
    Title         string
    Description   *string
    Genre         *string
    Style         string
    TotalEpisodes int
    TotalDuration int
    Status        string
    Thumbnail     *string
    Tags          datatypes.JSON
    Metadata      datatypes.JSON
    CreatedAt     time.Time
    UpdatedAt     time.Time
    DeletedAt     gorm.DeletedAt

    // 关联
    Episodes   []Episode
    Characters []Character
    Scenes     []Scene
}
```

### 2.2 Episode (章节)
```go
type Episode struct {
    ID            uint
    DramaID       uint
    EpisodeNum    int
    Title         string
    ScriptContent *string
    Description   *string
    Duration      int
    Status        string
    VideoURL      *string
    Thumbnail     *string
    CreatedAt     time.Time
    UpdatedAt     time.Time
    DeletedAt     gorm.DeletedAt

    // 关联
    Drama       Drama
    Storyboards []Storyboard
    Characters  []Character
    Scenes      []Scene
}
```

### 2.3 Character (角色)
```go
type Character struct {
    ID              uint
    DramaID         uint
    Name            string
    Role            *string
    Description     *string
    Appearance      *string
    Personality     *string
    VoiceStyle      *string
    ImageURL        *string
    ReferenceImages datatypes.JSON
    SeedValue       *string
    SortOrder       int
    CreatedAt       time.Time
    UpdatedAt       time.Time
    DeletedAt       gorm.DeletedAt

    // 关联
    Episodes []Episode

    // 运行时字段
    ImageGenerationStatus *string
    ImageGenerationError  *string
}
```

### 2.4 Storyboard (分镜)
```go
type Storyboard struct {
    ID               uint
    EpisodeID        uint
    SceneID          *uint
    StoryboardNumber int
    Title            *string
    Location         *string
    Time             *string
    ShotType         *string
    Angle            *string
    Movement         *string
    Action           *string
    Result           *string
    Atmosphere       *string
    ImagePrompt      *string
    VideoPrompt      *string
    BgmPrompt        *string
    SoundEffect      *string
    Dialogue         *string
    Description      *string
    Duration         int
    ComposedImage    *string
    VideoURL         *string
    Status           string
    CreatedAt        time.Time
    UpdatedAt        time.Time
    DeletedAt        gorm.DeletedAt

    // 关联
    Episode    Episode
    Background *Scene
    Characters []Character
}
```

### 2.5 Scene (场景)
```go
type Scene struct {
    ID                uint
    DramaID           uint
    EpisodeID         *uint
    Location          string
    Time              string
    Prompt            string
    StoryboardCount   int
    ImageURL          *string
    Status            string
    CreatedAt         time.Time
    UpdatedAt         time.Time
    DeletedAt         gorm.DeletedAt

    // 运行时字段
    ImageGenerationStatus *string
    ImageGenerationError  *string
}
```

### 2.6 ImageGeneration (图片生成记录)
```go
type ImageGeneration struct {
    ID              uint
    StoryboardID    *uint
    DramaID         uint
    SceneID         *uint
    CharacterID     *uint
    ImageType       string
    FrameType       *string
    Provider        string
    Prompt          string
    NegPrompt       *string
    Model           string
    Size            string
    Quality         string
    Style           *string
    Steps           *int
    CfgScale        *float64
    Seed            *int64
    ImageURL        *string
    MinioURL        *string
    LocalPath       *string
    Status          ImageGenerationStatus
    TaskID          *string
    ErrorMsg        *string
    Width           *int
    Height          *int
    ReferenceImages datatypes.JSON
    CreatedAt       time.Time
    UpdatedAt       time.Time
    CompletedAt     *time.Time

    // 关联
    Storyboard *Storyboard
    Drama      Drama
    Scene      *Scene
    Character  *Character
}
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

**AI 提供商**:
- `openai`: OpenAI DALL-E
- `midjourney`: Midjourney
- `stable_diffusion`: Stable Diffusion

### 2.7 VideoGeneration (视频生成记录)
```go
type VideoGeneration struct {
    ID                  uint
    StoryboardID        *uint
    DramaID             uint
    Provider            string
    Prompt              string
    Model               *string
    ImageGenID          *uint
    ReferenceMode       *string
    ImageURL            *string
    FirstFrameURL       *string
    LastFrameURL        *string
    ReferenceImageURLs  *string
    Duration            *int
    FPS                 *int
    Resolution          *string
    AspectRatio         *string
    Style               *string
    MotionLevel         *int
    CameraMotion        *string
    Seed                *int64
    VideoURL            *string
    MinioURL            *string
    LocalPath           *string
    Status              VideoStatus
    TaskID              *string
    ErrorMsg            *string
    CompletedAt         *time.Time
    Width               *int
    Height              *int
    CreatedAt           time.Time
    UpdatedAt           time.Time
    DeletedAt           gorm.DeletedAt

    // 关联
    Storyboard *Storyboard
    Drama      Drama
    ImageGen   ImageGeneration
}
```

**视频状态**: `pending`, `processing`, `completed`, `failed`

**视频提供商**:
- `runway`: RunwayML
- `pika`: Pika Labs
- `doubao`: 豆包
- `openai`: OpenAI Sora

### 2.8 VideoMerge (视频合并记录)
```go
type VideoMerge struct {
    ID          uint
    EpisodeID   uint
    DramaID     uint
    Title       string
    Provider    string
    Model       *string
    Status      VideoMergeStatus
    Scenes      datatypes.JSON
    MergedURL   *string
    Duration    *int
    TaskID      *string
    ErrorMsg    *string
    CreatedAt   time.Time
    CompletedAt *time.Time
    DeletedAt   gorm.DeletedAt

    // 关联
    Episode Episode
    Drama   Drama
}

type SceneClip struct {
    SceneID    uint
    VideoURL   string
    StartTime  float64
    EndTime    float64
    Duration   float64
    Order      int
    Transition map[string]interface{}
}
```

### 2.9 AsyncTask (异步任务)
```go
type AsyncTask struct {
    ID          string
    Type        string
    Status      string
    Progress    int
    Message     string
    Error       string
    Result      string
    ResourceID  string
    CreatedAt   time.Time
    UpdatedAt   time.Time
    CompletedAt *time.Time
    DeletedAt   gorm.DeletedAt
}
```

### 2.10 Asset (素材)
```go
type Asset struct {
    ID            uint
    DramaID       *uint
    EpisodeID     *uint
    StoryboardID  *uint
    StoryboardNum *int
    Name          string
    Description   *string
    Type          AssetType
    Category      *string
    URL           string
    ThumbnailURL  *string
    LocalPath     *string
    FileSize      *int64
    MimeType      *string
    Width         *int
    Height        *int
    Duration      *int
    Format        *string
    ImageGenID    *uint
    VideoGenID    *uint
    IsFavorite    bool
    ViewCount     int
    CreatedAt     time.Time
    UpdatedAt     time.Time
    DeletedAt     gorm.DeletedAt

    // 关联
    Drama     *Drama
    ImageGen  ImageGeneration
    VideoGen  VideoGeneration
}
```

**素材类型**: `image`, `video`, `audio`

---

## 3. 响应格式

### 3.1 统一响应结构
```go
type Response struct {
    Success   bool        `json:"success"`
    Data      interface{} `json:"data,omitempty"`
    Error     *ErrorInfo  `json:"error,omitempty"`
    Message   string      `json:"message,omitempty"`
    Timestamp string      `json:"timestamp"`
}

type ErrorInfo struct {
    Code    string      `json:"code"`
    Message string      `json:"message"`
    Details interface{} `json:"details,omitempty"`
}
```

### 3.2 分页响应
```go
type PaginationData struct {
    Items      interface{} `json:"items"`
    Pagination Pagination  `json:"pagination"`
}

type Pagination struct {
    Page       int   `json:"page"`
    PageSize   int   `json:"page_size"`
    Total      int64 `json:"total"`
    TotalPages int64 `json:"total_pages"`
}
```

### 3.3 响应函数
- `Success(c, data)` - 成功响应 (200)
- `SuccessWithMessage(c, message, data)` - 带消息的成功响应
- `Created(c, data)` - 创建成功响应 (201)
- `SuccessWithPagination(c, items, total, page, pageSize)` - 分页响应
- `BadRequest(c, message)` - 错误请求 (400)
- `Unauthorized(c, message)` - 未授权 (401)
- `Forbidden(c, message)` - 禁止访问 (403)
- `NotFound(c, message)` - 未找到 (404)
- `InternalError(c, message)` - 内部错误 (500)

---

## 4. 中间件

### 4.1 CORS 中间件
```go
func CORSMiddleware(allowedOrigins []string) gin.HandlerFunc
```

### 4.2 日志中间件
```go
func LoggerMiddleware(log *logger.Logger) gin.HandlerFunc
```

### 4.3 限流中间件
```go
func RateLimitMiddleware() gin.HandlerFunc
```

---

## 5. 服务层 (application/services)

| 服务 | 职责 |
|------|------|
| `AIService` | AI 配置管理 |
| `DramaService` | 剧本业务逻辑 |
| `ImageGenerationService` | 图片生成服务 |
| `VideoGenerationService` | 视频生成服务 |
| `VideoMergeService` | 视频合并服务 (FFmpeg) |
| `StoryboardService` | 分镜生成服务 |
| `CharacterLibraryService` | 角色库服务 |
| `TaskService` | 异步任务管理 |
| `AudioExtractionService` | 音频提取服务 (FFmpeg) |
| `AssetService` | 素材管理服务 |
| `ScriptGenerationService` | 脚本生成服务 |
| `UploadService` | 文件上传服务 |
| `ResourceTransferService` | 资源传输服务 |
| `FramePromptService` | 帧提示词生成服务 |

---

## 6. 外部集成

### 6.1 AI 客户端 (pkg/ai/)
- `client.go` - AI 客户端接口
- `openai_client.go` - OpenAI 客户端
- `gemini_client.go` - Gemini 客户端

### 6.2 图片生成 (pkg/image/)
- `image_client.go` - 图片生成接口
- `openai_image_client.go` - OpenAI DALL-E
- `volcengine_image_client.go` - 火山引擎
- `gemini_image_client.go` - Gemini

### 6.3 视频生成 (pkg/video/)
- `video_client.go` - 视频生成接口
- `openai_sora_client.go` - OpenAI Sora
- `minimax_client.go` - MiniMax
- `volces_ark_client.go` - 火山引擎
- `chatfire_client.go` - ChatFire

---

## 7. 关键特性

1. **统一响应格式**: 所有 API 返回统一的 JSON 结构
2. **异步任务处理**: 支持长时间运行的任务 (图片/视频生成)
3. **多 AI 提供商**: 支持多个 AI 服务提供商
4. **FFmpeg 集成**: 音频提取和视频合并
5. **分页支持**: 所有列表接口支持分页
6. **软删除**: 使用 GORM DeletedAt
7. **中间件**: CORS、日志、限流
8. **静态文件服务**: 本地存储 + MinIO

---

## 8. 配置项

主要配置在 `configs/config.example.yaml`:
- App: 应用名称、版本
- Server: 端口、CORS origins
- Database: 数据库连接
- Storage: 本地路径、Base URL
- AI: 默认提供商配置

---

## 9. 依赖

主要 Go 依赖:
- `gin-gonic/gin` - Web 框架
- `gorm.io/gorm` - ORM
- `gorm.io/driver/mysql` - MySQL 驱动
- `gorm.io/datatypes` - JSON 类型支持

---

## 10. 端口总结

**HTTP 端口**: 默认 8080
**静态文件**: `/static`
**API 前缀**: `/api/v1`
**健康检查**: `/health`
