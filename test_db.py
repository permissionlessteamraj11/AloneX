import asyncio
import logging
from NarzoxBots.database.db import db_instance as db
from NarzoxBots.database.redis import redis_cache

logging.basicConfig(level=logging.INFO)

async def test():
    try:
        await db.connect()
        print("MongoDB connection successful.")

        await db.add_user(12345, username="testuser", first_name="Test")
        user = await db.get_user(12345)
        if user and user.username == "testuser":
            print("User creation and retrieval successful.")
        else:
            print("User retrieval failed.")

        await redis_cache.set("test_key", "test_value")
        val = await redis_cache.get("test_key")
        if val == "test_value":
            print("Redis set and get successful.")
        else:
            print("Redis failed.")

    except Exception as e:
        print(f"Test failed with error: {e}")
    finally:
        if db.client:
            db.client.close()
        await redis_cache.close()

if __name__ == "__main__":
    asyncio.run(test())
