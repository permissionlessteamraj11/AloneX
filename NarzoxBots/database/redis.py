import redis.asyncio as redis
import logging
from config import Config

config = Config()
logger = logging.getLogger("NarzoxBots.Redis")

class RedisCache:
    def __init__(self):
        try:
            self.redis = redis.from_url(config.REDIS_URL, decode_responses=True)
            self._enabled = True
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._enabled = False

    async def set(self, key, value, ex=None):
        if not self._enabled: return
        try:
            await self.redis.set(key, value, ex=ex)
        except Exception as e:
            logger.error(f"Redis set error: {e}")

    async def get(self, key):
        if not self._enabled: return None
        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    async def delete(self, key):
        if not self._enabled: return
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")

    async def sadd(self, key, *values):
        if not self._enabled: return
        try:
            await self.redis.sadd(key, *values)
        except Exception as e:
            logger.error(f"Redis sadd error: {e}")

    async def smembers(self, key):
        if not self._enabled: return []
        try:
            return await self.redis.smembers(key)
        except Exception as e:
            logger.error(f"Redis smembers error: {e}")
            return []

    async def close(self):
        if not self._enabled: return
        try:
            await self.redis.close()
        except Exception as e:
            logger.error(f"Redis close error: {e}")

redis_cache = RedisCache()
