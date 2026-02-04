"""
FastAPI 应用入口

这是应用的根模块，负责：
1. 创建 FastAPI 应用实例
2. 配置中间件和异常处理器
3. 注册所有路由
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.middlewares.rate_limit import limiter

# 导入新的异常处理器
from src.exception_handlers import register_exception_handlers
from src.schemas import ApiResponse

# 导入新的路由（已迁移到 src）
from src.health import router as health_router
from src.settings import router as settings_router
from src.ai_configs import router as ai_configs_router
from src.character_library import router as character_library_router
from src.assets import router as assets_router

# 导入其他路由（暂时从 app 导入，后续会迁移）
from app.api.routes import (
    dramas, episodes, images, videos, tasks,
    upload, scenes, storyboards,
    video_merges, audio, script_generation
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    处理应用启动和关闭时的操作。
    """
    # 启动时创建必要的目录
    os.makedirs("./data", exist_ok=True)
    os.makedirs(settings.LOCAL_STORAGE_PATH, exist_ok=True)
    os.makedirs(settings.LOG_PATH, exist_ok=True)

    # 初始化数据库
    await init_db()

    yield

    # 关闭时的清理工作
    pass


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered drama generation platform",
    lifespan=lifespan,
)

# 配置速率限制器
app.state.limiter = limiter

# 注册全局异常处理器（使用新的统一响应格式）
register_exception_handlers(app)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件服务
app.mount("/static", StaticFiles(directory=settings.LOCAL_STORAGE_PATH), name="static")

# 注册所有路由
# 已迁移到 src 的路由
app.include_router(health_router, tags=["Health"])
app.include_router(settings_router, prefix="/api/v1/settings", tags=["Settings"])
app.include_router(ai_configs_router, prefix="/api/v1/ai-configs", tags=["AI Configs"])
app.include_router(character_library_router, prefix="/api/v1/character-library", tags=["Character Library"])
app.include_router(assets_router, prefix="/api/v1/assets", tags=["Assets"])
# 其他路由暂时从 app 导入，后续会迁移到 src 模块
app.include_router(dramas.router, prefix="/api/v1/dramas", tags=["Dramas"])
app.include_router(episodes.router, prefix="/api/v1/episodes", tags=["Episodes"])
app.include_router(images.router, prefix="/api/v1/images", tags=["Images"])
app.include_router(videos.router, prefix="/api/v1/videos", tags=["Videos"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(upload.router, prefix="/api/v1/upload", tags=["Upload"])
app.include_router(scenes.router, prefix="/api/v1/scenes", tags=["Scenes"])
app.include_router(storyboards.router, prefix="/api/v1/storyboards", tags=["Storyboards"])
app.include_router(video_merges.router, prefix="/api/v1/video-merges", tags=["Video Merges"])
app.include_router(audio.router, prefix="/api/v1/audio", tags=["Audio"])
app.include_router(assets.router, prefix="/api/v1/assets", tags=["Assets"])
app.include_router(script_generation.router, prefix="/api/v1/generation", tags=["Generation"])


@app.get("/", summary="根端点", response_model=ApiResponse)
async def root() -> ApiResponse:
    """
    API 根端点

    返回 API 欢迎信息和基本信息。

    Returns:
        ApiResponse: 包含应用名称、版本和文档链接的响应
    """
    return ApiResponse.success(data={
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    })


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
