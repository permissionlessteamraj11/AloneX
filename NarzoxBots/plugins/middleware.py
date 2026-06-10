# Copyright (c) 2025 NarzoxBots
# ALONE-CODER

import time
from pyrogram import Client, filters
from pyrogram.types import Message
from NarzoxBots.database.redis import redis_cache

RATE_LIMIT = 2 # seconds between commands

@Client.on_message(filters.regex(r"^/") & filters.group, group=-1)
async def rate_limit_middleware(client: Client, message: Message):
    if not message.from_user: return

    user_id = message.from_user.id
    key = f"rate_limit:{user_id}"

    last_cmd_time = await redis_cache.get(key)
    now = time.time()

    if last_cmd_time and now - float(last_cmd_time) < RATE_LIMIT:
        message.stop_propagation()
        # Optionally send a warning message
        return

    await redis_cache.set(key, now, ex=RATE_LIMIT)
