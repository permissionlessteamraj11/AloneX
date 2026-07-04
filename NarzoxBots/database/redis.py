import redis.asyncio as redis
import logging
from config import Config

config = Config()
logger = logging.getLogger("NarzoxBots.Redis")

class RedisCache:
    def __init__(self):
        self.redis = None
        self._enabled = False
        try:
            self.redis = redis.from_url(config.REDIS_URL, decode_responses=True)
            self._enabled = True
        except Exception as e:
            logger.warning(f"Redis not available at startup: {e}")

    def _handle_error(self, e):
        if self._enabled:
            logger.error(f"Redis error encountered: {e}. Disabling Redis cache.")
            self._enabled = False

    async def set(self, key, value, ex=None):
        if not self._enabled: return
        try:
            await self.redis.set(key, value, ex=ex)
        except Exception as e:
            self._handle_error(e)

    async def get(self, key):
        if not self._enabled: return None
        try:
            return await self.redis.get(key)
        except Exception as e:
            self._handle_error(e)
            return None

    async def delete(self, key):
        if not self._enabled: return
        try:
            await self.redis.delete(key)
        except Exception as e:
            self._handle_error(e)

    async def sadd(self, key, *values):
        if not self._enabled: return
        try:
            await self.redis.sadd(key, *values)
        except Exception as e:
            self._handle_error(e)

    async def smembers(self, key):
        if not self._enabled: return []
        try:
            return await self.redis.smembers(key)
        except Exception as e:
            self._handle_error(e)
            return []

    async def close(self):
        if not self._enabled or not self.redis: return
        try:
            await self.redis.close()
        except Exception as e:
            logger.error(f"Redis close error: {e}")

redis_cache = RedisCache()
