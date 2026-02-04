"""
全局应用配置

该模块定义了应用程序的全局配置，包括数据库、存储、CORS 等设置。
使用 Pydantic BaseSettings 从环境变量读取配置。
"""
from typing import List, Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用全局配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    # ========== 应用信息 ==========
    APP_NAME: str = "huobao-drama"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    LANGUAGE: str = "zh-CN"

    # ========== 服务器配置 ==========
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ========== CORS 配置 ==========
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:5174"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """解析 CORS 来源，支持逗号分隔的字符串"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ========== 数据库配置 ==========
    DATABASE_TYPE: str = "sqlite"
    SQLITE_PATH: str = "./data/drama.db"
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[int] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None

    @property
    def DATABASE_URL(self) -> str:
        """获取数据库 URL，根据类型自动选择"""
        if self.DATABASE_TYPE == "postgresql":
            return (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return f"sqlite+aiosqlite:///{self.SQLITE_PATH}"

    # ========== 存储配置 ==========
    STORAGE_TYPE: str = "local"
    LOCAL_STORAGE_PATH: str = "./uploads"
    BASE_URL: str = "/static"

    # ========== AI 配置 ==========
    DEFAULT_AI_PROVIDER: str = "openai"

    # ========== 日志配置 ==========
    LOG_LEVEL: str = "INFO"
    LOG_PATH: str = "./logs"

    # ========== 安全配置 ==========
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ========== Redis 配置（可选）==========
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None
    REDIS_DB: Optional[int] = None

    @property
    def REDIS_URL(self) -> Optional[str]:
        """获取 Redis URL"""
        if self.REDIS_HOST and self.REDIS_PORT:
            return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB or 0}"
        return None


# 全局配置实例
settings = Settings()
