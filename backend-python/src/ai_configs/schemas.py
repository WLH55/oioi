"""
AI 配置请求/响应模型

定义 AI 配置相关的 Pydantic 模型。
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
import json


class AIServiceConfigBase(BaseModel):
    """AI 服务配置基础模型"""
    service_type: str = Field(..., pattern="^(text|image|video)$", description="服务类型")
    name: str = Field(..., min_length=1, max_length=100, description="配置名称")
    provider: str = Field(..., description="AI 提供商")
    base_url: str = Field(..., description="API 基础 URL")
    model: List[str] = Field(..., description="支持的模型列表")
    endpoint: Optional[str] = Field(None, description="API 端点")
    query_endpoint: Optional[str] = Field(None, description="查询端点")
    priority: int = Field(default=0, description="优先级")
    is_default: bool = Field(default=False, description="是否为默认配置")
    settings: Optional[str] = Field(None, description="额外设置（JSON 字符串）")


class AIServiceConfigCreate(AIServiceConfigBase):
    """创建 AI 服务配置请求"""
    api_key: str = Field(..., description="API 密钥")


class AIServiceConfigUpdate(BaseModel):
    """更新 AI 服务配置请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    provider: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[List[str]] = None
    endpoint: Optional[str] = None
    query_endpoint: Optional[str] = None
    priority: Optional[int] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    settings: Optional[str] = None


class AIServiceConfigResponse(AIServiceConfigBase):
    """AI 服务配置响应"""
    id: int
    api_key: str  # 生产环境可能需要屏蔽
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TestConnectionRequest(BaseModel):
    """测试连接请求"""
    base_url: str = Field(..., description="API 基础 URL")
    api_key: str = Field(..., description="API 密钥")
    model: List[str] = Field(..., description="模型列表")
    provider: Optional[str] = Field(None, description="提供商")
    endpoint: Optional[str] = Field(None, description="端点")
