from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import select, delete, update
from config import Config
from .models import Base, User, Chat, Clone, CloneSettings, GlobalSettings, Broadcast, AuthUser

config = Config()

engine = create_async_engine(config.POSTGRES_URL, echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Database:
    def __init__(self):
        self.active_calls = {}
        self.notified = set()
        self.bl_users = set()
        self.sudoers = set()
        self.admins = {}

    async def connect(self):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await self.load_cache()

    async def load_cache(self):
        async with async_session() as session:
            # Load Sudoers
            res = await session.execute(select(User.id).where(User.is_sudo == True))
            self.sudoers = set(res.scalars().all())
            self.sudoers.add(config.OWNER_ID)

            # Load Blacklisted Users
            res = await session.execute(select(User.id).where(User.is_suspended == True))
            self.bl_users = set(res.scalars().all())

    async def get_call(self, chat_id: int):
        return chat_id in self.active_calls

    async def add_call(self, chat_id: int):
        self.active_calls[chat_id] = 1

    async def remove_call(self, chat_id: int):
        self.active_calls.pop(chat_id, None)

    async def playing(self, chat_id: int, paused: bool = None):
        if paused is not None:
            self.active_calls[chat_id] = 0 if paused else 1
        return bool(self.active_calls.get(chat_id, 0))

    # User Management
    async def is_user(self, user_id: int):
        async with async_session() as session:
            res = await session.execute(select(User).where(User.id == user_id))
            return res.scalar_one_or_none() is not None

    async def add_user(self, user_id: int):
        async with async_session() as session:
            if not await self.is_user(user_id):
                session.add(User(id=user_id))
                await session.commit()

    async def get_users(self):
        async with async_session() as session:
            res = await session.execute(select(User.id))
            return res.scalars().all()

    # Chat Management
    async def is_chat(self, chat_id: int):
        async with async_session() as session:
            res = await session.execute(select(Chat).where(Chat.id == chat_id))
            return res.scalar_one_or_none() is not None

    async def add_chat(self, chat_id: int):
        async with async_session() as session:
            if not await self.is_chat(chat_id):
                session.add(Chat(id=chat_id))
                await session.commit()

    async def get_chats(self):
        async with async_session() as session:
            res = await session.execute(select(Chat.id))
            return res.scalars().all()

    async def get_lang(self, chat_id: int):
        async with async_session() as session:
            res = await session.execute(select(Chat.lang).where(Chat.id == chat_id))
            return res.scalar() or "en"

    async def set_lang(self, chat_id: int, lang: str):
        async with async_session() as session:
            await session.execute(update(Chat).where(Chat.id == chat_id).values(lang=lang))
            await session.commit()

    async def get_play_mode(self, chat_id: int):
        async with async_session() as session:
            res = await session.execute(select(Chat.admin_only).where(Chat.id == chat_id))
            return res.scalar() or False

    async def set_play_mode(self, chat_id: int, admin_only: bool):
        async with async_session() as session:
            await session.execute(update(Chat).where(Chat.id == chat_id).values(admin_only=admin_only))
            await session.commit()

    async def get_cmd_delete(self, chat_id: int):
        async with async_session() as session:
            res = await session.execute(select(Chat.cmd_delete).where(Chat.id == chat_id))
            return res.scalar() or False

    async def set_cmd_delete(self, chat_id: int, cmd_delete: bool):
        async with async_session() as session:
            await session.execute(update(Chat).where(Chat.id == chat_id).values(cmd_delete=cmd_delete))
            await session.commit()

    # Sudo Management
    async def add_sudo(self, user_id: int):
        async with async_session() as session:
            await session.execute(update(User).where(User.id == user_id).values(is_sudo=True))
            await session.commit()
            self.sudoers.add(user_id)

    async def del_sudo(self, user_id: int):
        async with async_session() as session:
            await session.execute(update(User).where(User.id == user_id).values(is_sudo=False))
            await session.commit()
            self.sudoers.discard(user_id)

    async def get_sudoers(self):
        return list(self.sudoers)

    # Auth Management
    async def is_auth(self, chat_id: int, user_id: int):
        async with async_session() as session:
            res = await session.execute(
                select(AuthUser).where(AuthUser.chat_id == chat_id, AuthUser.user_id == user_id)
            )
            return res.scalar_one_or_none() is not None

    async def add_auth(self, chat_id: int, user_id: int):
        async with async_session() as session:
            if not await self.is_auth(chat_id, user_id):
                session.add(AuthUser(chat_id=chat_id, user_id=user_id))
                await session.commit()

    async def rm_auth(self, chat_id: int, user_id: int):
        async with async_session() as session:
            await session.execute(
                delete(AuthUser).where(AuthUser.chat_id == chat_id, AuthUser.user_id == user_id)
            )
            await session.commit()

    # Admin Management
    async def get_admins(self, chat_id: int, reload: bool = False):
        if chat_id not in self.admins or reload:
            from NarzoxBots.helpers import reload_admins
            self.admins[chat_id] = await reload_admins(chat_id)
        return self.admins[chat_id]

    # Blacklist Management
    async def add_blacklist(self, target_id: int):
        async with async_session() as session:
            if str(target_id).startswith("-100"):
                await session.execute(update(Chat).where(Chat.id == target_id).values(is_blacklisted=True))
            else:
                await session.execute(update(User).where(User.id == target_id).values(is_suspended=True))
            await session.commit()
            self.bl_users.add(target_id)

    async def del_blacklist(self, target_id: int):
        async with async_session() as session:
            if str(target_id).startswith("-100"):
                await session.execute(update(Chat).where(Chat.id == target_id).values(is_blacklisted=False))
            else:
                await session.execute(update(User).where(User.id == target_id).values(is_suspended=False))
            await session.commit()
            self.bl_users.discard(target_id)

    @property
    def blacklisted(self):
        return self.bl_users

    async def get_blacklisted(self):
        return list(self.bl_users)

    # Logger
    async def is_logger(self):
        # This seems to be a toggle for enabling/disabling logging in some contexts
        # For now, we'll return True if LOGGER_ID is set
        return bool(config.LOGGER_ID)

    async def get_assistant(self, chat_id: int):
        from NarzoxBots import userbot
        return userbot.clients[0]

    async def get_client(self, chat_id: int):
        return await self.get_assistant(chat_id)

async def get_db():
    async with async_session() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

db_instance = Database()
