"""High-performance caching service for ultra-fast responses."""
import logging
from typing import Optional, Dict, Any
import redis.asyncio as redis
from datetime import timedelta
import json

logger = logging.getLogger(__name__)


class CacheManager:
    """High-performance cache manager with Redis."""

    def __init__(self, redis_url: str):
        """Initialize cache manager.
        
        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self._is_connected = False

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.redis = await redis.from_url(self.redis_url, decode_responses=True)
            await self.redis.ping()
            self._is_connected = True
            logger.info("✅ Cache connected")
        except Exception as e:
            logger.error(f"Cache connection error: {str(e)}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            self._is_connected = False

    async def get(self, key: str) -> Optional[Any]:
        """Get cached value.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if not self._is_connected:
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                try:
                    return json.loads(value)
                except:
                    return value
            return None
        except Exception as e:
            logger.debug(f"Cache get error: {str(e)}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set cached value.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            Success status
        """
        if not self._is_connected:
            return False
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            await self.redis.setex(
                key,
                timedelta(seconds=ttl),
                str(value)
            )
            return True
        except Exception as e:
            logger.debug(f"Cache set error: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete cached value.
        
        Args:
            key: Cache key
            
        Returns:
            Success status
        """
        if not self._is_connected:
            return False
        
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.debug(f"Cache delete error: {str(e)}")
            return False

    async def get_or_set(self, key: str, fetch_fn, ttl: int = 3600) -> Any:
        """Get value from cache or fetch and cache it.
        
        Args:
            key: Cache key
            fetch_fn: Async function to fetch value
            ttl: Time to live in seconds
            
        Returns:
            Cached or fetched value
        """
        # Try to get from cache
        cached = await self.get(key)
        if cached is not None:
            logger.debug(f"Cache hit: {key}")
            return cached
        
        # Fetch and cache
        logger.debug(f"Cache miss: {key}")
        value = await fetch_fn()
        await self.set(key, value, ttl)
        return value

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern.
        
        Args:
            pattern: Key pattern (e.g., "queue:*")
            
        Returns:
            Number of deleted keys
        """
        if not self._is_connected:
            return 0
        
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.debug(f"Cache clear error: {str(e)}")
            return 0

    @property
    def is_connected(self) -> bool:
        """Check if cache is connected."""
        return self._is_connected
