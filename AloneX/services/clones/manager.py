import asyncio
from pyrogram import Client, filters
from AloneX import config, logger
from AloneX.database.db import async_session
from AloneX.database.models import Clone, User
from AloneX.services.encryption import encryption_service
from sqlalchemy import select

class CloneManager:
    def __init__(self):
        self.clones = {} # bot_token: Client

    async def start_clone(self, bot_token: str, encrypted: bool = False):
        if encrypted:
            bot_token = encryption_service.decrypt(bot_token)

        if bot_token in self.clones:
            return self.clones[bot_token]

        client = Client(
            name=f"clone_{bot_token.split(':')[0]}",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=bot_token,
            plugins=dict(root="AloneX.plugins") # Reuse existing plugins
        )

        try:
            await client.start()
            self.clones[bot_token] = client
            logger.info(f"Started clone: @{client.me.username}")
            return client
        except Exception as e:
            logger.error(f"Failed to start clone with token {bot_token[:10]}...: {e}")
            return None

    async def stop_clone(self, bot_token: str):
        if bot_token in self.clones:
            client = self.clones.pop(bot_token)
            await client.stop()
            logger.info(f"Stopped clone: @{client.me.username}")

    async def load_all_clones(self):
        async with async_session() as session:
            result = await session.execute(select(Clone).where(Clone.status == "active"))
            clones = result.scalars().all()
            for clone in clones:
                await self.start_clone(clone.bot_token, encrypted=True)

clone_manager = CloneManager()
