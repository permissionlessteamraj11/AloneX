import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from config import Config
from .models import User, Chat, Clone, CloneSettings, GlobalSettings
from .redis import redis_cache

config = Config()
logger = logging.getLogger("NarzoxBots.DB")

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.active_calls = {}
        self.sudoers = set()
        self.bl_users = set()
        self.admins = {}
        self.notified = set()

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(config.MONGO_URL)
            self.db = self.client["NarzoxMusic"]
            logger.info("Connected to MongoDB.")
            await self.load_cache()
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def load_cache(self):
        # Load Sudoers
        sudoers_cursor = self.db.users.find({"is_sudo": True})
        async for user in sudoers_cursor:
            self.sudoers.add(int(user["_id"]))
        self.sudoers.add(config.OWNER_ID)

        # Load Blacklisted
        bl_cursor = self.db.users.find({"is_suspended": True})
        async for user in bl_cursor:
            self.bl_users.add(int(user["_id"]))

        bl_chats_cursor = self.db.chats.find({"is_blacklisted": True})
        async for chat in bl_chats_cursor:
            self.bl_users.add(int(chat["_id"]))

        logger.info(f"Cache loaded: {len(self.sudoers)} sudoers, {len(self.bl_users)} blacklisted.")

    # User Management
    async def get_user(self, user_id: int):
        data = await self.db.users.find_one({"_id": user_id})
        return User.from_dict(data) if data else None

    async def add_user(self, user_id: int, **kwargs):
        if not await self.get_user(user_id):
            user = User(id=user_id, **kwargs)
            await self.db.users.insert_one(user.to_dict())

    async def update_user(self, user_id: int, **kwargs):
        await self.db.users.update_one({"_id": user_id}, {"$set": kwargs})

    # Chat Management
    async def get_chat(self, chat_id: int):
        data = await self.db.chats.find_one({"_id": chat_id})
        return Chat.from_dict(data) if data else None

    async def add_chat(self, chat_id: int):
        if not await self.get_chat(chat_id):
            chat = Chat(id=chat_id)
            await self.db.chats.insert_one(chat.to_dict())

    async def set_lang(self, chat_id: int, lang: str):
        await self.db.chats.update_one({"_id": chat_id}, {"$set": {"lang": lang}})

    async def get_lang(self, chat_id: int):
        chat = await self.get_chat(chat_id)
        return chat.lang if chat else "en"

    # Auth Management
    async def is_auth(self, chat_id: int, user_id: int) -> bool:
        chat = await self.get_chat(chat_id)
        return user_id in chat.auth_users if chat else False

    async def add_auth(self, chat_id: int, user_id: int):
        await self.db.chats.update_one(
            {"_id": chat_id}, {"$addToSet": {"auth_users": user_id}}, upsert=True
        )

    async def rm_auth(self, chat_id: int, user_id: int):
        await self.db.chats.update_one(
            {"_id": chat_id}, {"$pull": {"auth_users": user_id}}
        )

    # Admin Management
    async def get_admins(self, chat_id: int, reload: bool = False) -> list[int]:
        if not reload and chat_id in self.admins:
            return self.admins[chat_id]

        from NarzoxBots.helpers._admins import reload_admins
        admins = await reload_admins(chat_id)
        if admins:
            self.admins[chat_id] = admins
        return admins

    # Warning Management
    async def add_warn(self, chat_id: int, user_id: int) -> int:
        key = f"warns:{chat_id}:{user_id}"
        warns = await redis_cache.get(key)
        warns = int(warns) + 1 if warns else 1
        await redis_cache.set(key, warns)
        return warns

    async def get_warns(self, chat_id: int, user_id: int) -> int:
        key = f"warns:{chat_id}:{user_id}"
        warns = await redis_cache.get(key)
        return int(warns) if warns else 0

    async def reset_warns(self, chat_id: int, user_id: int):
        key = f"warns:{chat_id}:{user_id}"
        await redis_cache.delete(key)

    # Call Management (In-memory/Redis preferred for real-time)
    async def add_call(self, chat_id: int):
        self.active_calls[chat_id] = 1

    async def remove_call(self, chat_id: int):
        self.active_calls.pop(chat_id, None)

    async def get_call(self, chat_id: int):
        return chat_id in self.active_calls

    async def playing(self, chat_id: int, paused: bool = None):
        if paused is not None:
            self.active_calls[chat_id] = 0 if paused else 1
        return bool(self.active_calls.get(chat_id, 0))

    # Feature Flags / Settings
    async def get_feature_flag(self, flag_name: str, clone_id: str = None) -> bool:
        if clone_id:
            data = await self.db.clone_settings.find_one({"_id": int(clone_id)})
            if data:
                return data.get(flag_name, True)

        data = await self.db.global_settings.find_one({"_id": 1})
        return data.get(flag_name, True) if data else True

    async def get_settings(self, clone_id: str = None):
        if clone_id:
            data = await self.db.clone_settings.find_one({"_id": int(clone_id)})
            return CloneSettings.from_dict(data) if data else None

        data = await self.db.global_settings.find_one({"_id": 1})
        return GlobalSettings.from_dict(data) if data else None

    async def get_clones(self):
        cursor = self.db.clones.find({})
        clones = {}
        async for clone in cursor:
            clones[str(clone["_id"])] = clone
        return clones

    async def get_all_users(self):
        cursor = self.db.users.find({})
        users = []
        async for user in cursor:
            users.append(user["_id"])
        return users

    async def get_all_chats(self):
        cursor = self.db.chats.find({})
        chats = []
        async for chat in cursor:
            chats.append(chat["_id"])
        return chats

    async def is_chat(self, chat_id: int):
        return await self.db.chats.find_one({"_id": chat_id}) is not None

    async def get_play_mode(self, chat_id: int):
        chat = await self.get_chat(chat_id)
        return chat.admin_only if chat else False

    async def get_cmd_delete(self, chat_id: int):
        chat = await self.get_chat(chat_id)
        return chat.cmd_delete if chat else False

    async def update_settings(self, clone_id: str, **kwargs):
        if clone_id:
            await self.db.clone_settings.update_one({"_id": int(clone_id)}, {"$set": kwargs}, upsert=True)
        else:
            await self.db.global_settings.update_one({"_id": 1}, {"$set": kwargs}, upsert=True)

    # Assistant & Client resolution
    async def get_assistant(self, chat_id: int, bot_id: int = None):
        from NarzoxBots.services.clones.manager import clone_manager
        if bot_id:
            for token, client in clone_manager.clones.items():
                if client.me and client.me.id == bot_id:
                    assistant = clone_manager.assistants.get(token)
                    if assistant: return assistant

        from NarzoxBots import userbot
        return userbot.clients[0]

    async def get_client(self, chat_id: int, bot_id: int = None):
        from NarzoxBots import app
        from NarzoxBots.services.clones.manager import clone_manager
        if bot_id:
            if bot_id == app.id: return app
            for client in clone_manager.clones.values():
                if client.me and client.me.id == bot_id: return client
        return app

    # Blacklist/Sudo Helpers
    async def add_sudo(self, user_id: int):
        await self.update_user(user_id, is_sudo=True)
        self.sudoers.add(user_id)

    async def del_sudo(self, user_id: int):
        await self.update_user(user_id, is_sudo=False)
        self.sudoers.discard(user_id)

    async def get_sudoers(self):
        return list(self.sudoers)

    @property
    def blacklisted(self):
        return self.bl_users

    async def add_blacklist(self, chat_id: int):
        if chat_id > 0: # User
            await self.update_user(chat_id, is_suspended=True)
        else: # Group
            await self.db.chats.update_one({"_id": chat_id}, {"$set": {"is_blacklisted": True}}, upsert=True)
        self.bl_users.add(chat_id)

    async def del_blacklist(self, chat_id: int):
        if chat_id > 0: # User
            await self.update_user(chat_id, is_suspended=False)
        else: # Group
            await self.db.chats.update_one({"_id": chat_id}, {"$set": {"is_blacklisted": False}})
        self.bl_users.discard(chat_id)

db_instance = Database()
