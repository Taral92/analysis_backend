"""
Redis caching utilities for performance optimization.
"""
import redis
import json
from typing import Any, Optional, Callable
from functools import wraps
from app.config import settings

# Initialize Redis client
redis_client = None

if settings.CACHE_ENABLED:
    try:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            decode_responses=True
        )
        redis_client.ping()
        print("✅ Redis connected successfully")
    except Exception as e:
        print(f"⚠️ Redis connection failed: {e}")
        redis_client = None


def get_cache(key: str) -> Optional[Any]:
    """Get value from cache."""
    if not redis_client or not settings.CACHE_ENABLED:
        return None
    
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
    except Exception as e:
        print(f"Cache get error: {e}")
    
    return None


def set_cache(key: str, value: Any, ttl: int = None) -> bool:
    """Set value in cache with TTL."""
    if not redis_client or not settings.CACHE_ENABLED:
        return False
    
    try:
        ttl = ttl or settings.CACHE_TTL
        redis_client.setex(key, ttl, json.dumps(value))
        return True
    except Exception as e:
        print(f"Cache set error: {e}")
        return False


def delete_cache(key: str) -> bool:
    """Delete key from cache."""
    if not redis_client or not settings.CACHE_ENABLED:
        return False
    
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Cache delete error: {e}")
        return False


def clear_cache_pattern(pattern: str) -> int:
    """Delete all keys matching pattern."""
    if not redis_client or not settings.CACHE_ENABLED:
        return 0
    
    try:
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
    except Exception as e:
        print(f"Cache clear error: {e}")
    
    return 0


def cached(ttl: int = None, key_prefix: str = ""):
    """
    Decorator for caching function results.
    
    Usage:
        @cached(ttl=300, key_prefix="analytics")
        def expensive_function(param1, param2):
            return result
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached_result = get_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            set_cache(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator
