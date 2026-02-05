"""
速率限制中间件

使用 slowapi 实现 API 速率限制。
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# 创建速率限制器
limiter = Limiter(key_func=get_remote_address)
