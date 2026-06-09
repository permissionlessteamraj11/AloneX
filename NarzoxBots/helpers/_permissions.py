# Copyright (c) 2025 NarzoxBots
# Licensed under the MIT License.

from pyrogram import enums
from pyrogram.types import Message
from NarzoxBots import app, config, db

class Permission:
    @staticmethod
    async def is_owner(user_id: int) -> bool:
        return user_id == config.OWNER_ID

    @staticmethod
    async def is_sudo(user_id: int) -> bool:
        return user_id in app.sudoers

    @staticmethod
    async def is_auth(chat_id: int, user_id: int) -> bool:
        return await db.is_auth(chat_id, user_id)

    @staticmethod
    async def is_admin(chat_id: int, user_id: int) -> bool:
        try:
            admins = await db.get_admins(chat_id)
            return user_id in admins
        except:
            return False

    @classmethod
    async def check_permission(cls, chat_id: int, user_id: int, level: str = "admin") -> bool:
        if await cls.is_owner(user_id):
            return True
        if await cls.is_sudo(user_id):
            return True

        if level == "auth":
            return await cls.is_auth(chat_id, user_id) or await cls.is_admin(chat_id, user_id)

        if level == "admin":
            return await cls.is_admin(chat_id, user_id)

        return False

def require_permission(level="admin"):
    from functools import wraps
    def decorator(func):
        @wraps(func)
        async def wrapper(client, message, *args, **kwargs):
            if not message.from_user:
                return

            chat_id = message.chat.id
            user_id = message.from_user.id

            if not await permission.check_permission(chat_id, user_id, level=level):
                return await message.reply_text(message.lang.get("play_admin", "Unauthorized"))

            return await func(client, message, *args, **kwargs)
        return wrapper
    return decorator

permission = Permission()
