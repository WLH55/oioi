from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import init_db
from app.core.exceptions import APIException
from app.core.exception_handlers import (
    api_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from app.middlewares.rate_limit import limiter
from app.api.routes import (
    health, dramas, episodes, ai_configs, images, videos, tasks,
    character_library, upload, scenes, storyboards,
    video_merges, audio, assets, settings, script_generation
)
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    # Create data directory if it doesn't exist
    os.makedirs("./data", exist_ok=True)
    os.makedirs(settings.LOCAL_STORAGE_PATH, exist_ok=True)
    os.makedirs(settings.LOG_PATH, exist_ok=True)

    # Initialize database
    await init_db()

    yield

    # Shutdown
    pass


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered drama generation platform",
    lifespan=lifespan,
)

# Set up rate limiter
app.state.limiter = limiter

# Register exception handlers for unified response format
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=settings.LOCAL_STORAGE_PATH), name="static")

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(dramas.router, prefix="/api/v1/dramas", tags=["Dramas"])
app.include_router(episodes.router, prefix="/api/v1/episodes", tags=["Episodes"])
app.include_router(ai_configs.router, prefix="/api/v1/ai-configs", tags=["AI Configs"])
app.include_router(images.router, prefix="/api/v1/images", tags=["Images"])
app.include_router(videos.router, prefix="/api/v1/videos", tags=["Videos"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])

# New routers
app.include_router(character_library.router, prefix="/api/v1/character-library", tags=["Character Library"])
app.include_router(upload.router, prefix="/api/v1/upload", tags=["Upload"])
app.include_router(scenes.router, prefix="/api/v1/scenes", tags=["Scenes"])
app.include_router(storyboards.router, prefix="/api/v1/storyboards", tags=["Storyboards"])
app.include_router(video_merges.router, prefix="/api/v1/video-merges", tags=["Video Merges"])
app.include_router(audio.router, prefix="/api/v1/audio", tags=["Audio"])
app.include_router(assets.router, prefix="/api/v1/assets", tags=["Assets"])
app.include_router(settings.router, prefix="/api/v1/settings", tags=["Settings"])
app.include_router(script_generation.router, prefix="/api/v1/generation", tags=["Generation"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
