import redis.asyncio as redis
from config import Config

config = Config()

class RedisCache:
    def __init__(self):
        self.redis = redis.from_url(config.REDIS_URL, decode_responses=True)

    async def set(self, key, value, ex=None):
        await self.redis.set(key, value, ex=ex)

    async def get(self, key):
        return await self.redis.get(key)

    async def delete(self, key):
        await self.redis.delete(key)

    async def sadd(self, key, *values):
        await self.redis.sadd(key, *values)

    async def smembers(self, key):
        return await self.redis.smembers(key)

    async def close(self):
        await self.redis.close()

redis_cache = RedisCache()
