"""Caching layer with memory and Redis backends"""

import hashlib
import json
from abc import ABC, abstractmethod
from typing import Any

import structlog
from aiocache import Cache
from aiocache.serializers import PickleSerializer

from bdfinance.config import CacheConfig

logger = structlog.get_logger()


class CacheBackend(ABC):
    """Abstract cache backend"""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Get value from cache"""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int) -> None:
        """Set value in cache with TTL"""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all cache entries"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close cache connection"""
        pass


class MemoryCache(CacheBackend):
    """In-memory cache backend using aiocache"""

    def __init__(self, config: CacheConfig) -> None:
        self.config = config
        self.cache = Cache(
            Cache.MEMORY,
            ttl=config.ttl,
            serializer=PickleSerializer(),
        )
        logger.info("Memory cache initialized", ttl=config.ttl)

    async def get(self, key: str) -> Any | None:
        """Get value from cache"""
        value = await self.cache.get(key)
        if value is not None:
            logger.debug("Cache hit", key=key)
        else:
            logger.debug("Cache miss", key=key)
        return value

    async def set(self, key: str, value: Any, ttl: int) -> None:
        """Set value in cache with TTL"""
        await self.cache.set(key, value, ttl=ttl)
        logger.debug("Cache set", key=key, ttl=ttl)

    async def clear(self) -> None:
        """Clear all cache entries"""
        await self.cache.clear()
        logger.info("Cache cleared")

    async def close(self) -> None:
        """Close cache connection"""
        await self.cache.close()


class RedisCache(CacheBackend):
    """Redis cache backend using aiocache"""

    def __init__(self, config: CacheConfig) -> None:
        self.config = config
        self.cache = Cache(
            Cache.REDIS,  # type: ignore
            endpoint=self._parse_redis_url(config.redis_url),
            ttl=config.ttl,
            serializer=PickleSerializer(),
        )
        logger.info("Redis cache initialized", url=config.redis_url, ttl=config.ttl)

    def _parse_redis_url(self, url: str) -> tuple[str, int]:
        """Parse Redis URL to (host, port)"""
        # Simple parsing: redis://host:port/db
        parts = url.replace("redis://", "").split("/")[0].split(":")
        host = parts[0] if len(parts) > 0 else "localhost"
        port = int(parts[1]) if len(parts) > 1 else 6379
        return (host, port)

    async def get(self, key: str) -> Any | None:
        """Get value from cache"""
        value = await self.cache.get(key)  # type: ignore
        if value is not None:
            logger.debug("Cache hit", key=key)
        else:
            logger.debug("Cache miss", key=key)
        return value

    async def set(self, key: str, value: Any, ttl: int) -> None:
        """Set value in cache with TTL"""
        await self.cache.set(key, value, ttl=ttl)  # type: ignore
        logger.debug("Cache set", key=key, ttl=ttl)

    async def clear(self) -> None:
        """Clear all cache entries"""
        await self.cache.clear()  # type: ignore
        logger.info("Cache cleared")

    async def close(self) -> None:
        """Close cache connection"""
        await self.cache.close()  # type: ignore


def default(obj: Any) -> Any:
    """Default JSON serializer for non-serializable objects"""
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    elif hasattr(obj, "model_dump"):
        return obj.model_dump()
    elif isinstance(obj, (set, frozenset)):
        return list(obj)
    elif hasattr(obj, "__dict__"):
        return obj.__dict__
    else:
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class CacheManager:
    """Cache manager with key generation and backend abstraction"""

    def __init__(self, config: CacheConfig) -> None:
        self.config = config
        self.backend: CacheBackend

        if config.backend == "redis":
            self.backend = RedisCache(config)
        else:
            self.backend = MemoryCache(config)

    def generate_key(self, prefix: str, **kwargs: Any) -> str:
        """Generate a unique cache key from prefix and kwargs"""
        # Sort kwargs for consistent key generation
        sorted_kwargs = sorted(kwargs.items())
        key_data = f"{prefix}:{json.dumps(sorted_kwargs, sort_keys=True, default=default)}"
        # Use hash for shorter keys
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"bdfinance:{prefix}:{key_hash}"

    async def get(self, prefix: str, **kwargs: Any) -> Any | None:
        """Get value from cache"""
        key = self.generate_key(prefix, **kwargs)
        return await self.backend.get(key)

    async def set(self, prefix: str, value: Any, ttl: int | None = None, **kwargs: Any) -> None:
        """Set value in cache with TTL"""
        key = self.generate_key(prefix, **kwargs)
        ttl = ttl or self.config.ttl
        await self.backend.set(key, value, ttl)

    async def clear(self) -> None:
        """Clear all cache entries"""
        await self.backend.clear()

    async def close(self) -> None:
        """Close cache connection"""
        await self.backend.close()
