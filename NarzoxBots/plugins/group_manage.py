# Copyright (c) 2025 NarzoxBots
# ALONE-CODER

import time
from pyrogram import filters, Client
from pyrogram.types import Message
from NarzoxBots import app, db, logger
from NarzoxBots.database.redis import redis_cache

@Client.on_message(filters.new_chat_members)
async def auto_welcome(client: Client, message: Message):
    try:
        chat = await db.get_chat(message.chat.id)
        if not chat or not chat.settings.get("welcome_enabled"): return
        for user in message.new_chat_members:
            if user.id == client.me.id: continue
            welcome_text = chat.settings.get("welcome_text", f"Welcome {user.mention}!")
            await message.reply_text(welcome_text)
    except Exception as e:
        logger.error(f"Auto-Welcome Error: {e}")

@Client.on_message(filters.group & ~filters.service, group=0)
async def anti_flood(client: Client, message: Message):
    if not message.from_user: return
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id

        key = f"flood:{chat_id}:{user_id}"
        count = await redis_cache.get(key) or 0
        count = int(count) + 1
        await redis_cache.set(key, count, ex=5)

        if count > 5:
            await client.ban_chat_member(chat_id, user_id)
            await message.reply_text(f"Banned {message.from_user.mention} for flooding.")
    except Exception as e:
        logger.error(f"Anti-Flood Error: {e}")

@Client.on_message(filters.group & ~filters.service, group=1)
async def word_filter(client: Client, message: Message):
    try:
        chat = await db.get_chat(message.chat.id)
        if not chat: return
        words = chat.settings.get("word_filter", [])
        text = message.text or message.caption or ""
        if any(w.lower() in text.lower() for w in words):
            await message.delete()
    except Exception as e:
        logger.error(f"Word Filter Error: {e}")
