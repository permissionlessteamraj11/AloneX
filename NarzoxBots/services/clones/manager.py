import asyncio
from pyrogram import Client, filters
from NarzoxBots import config, logger
from NarzoxBots.database.db import async_session
from NarzoxBots.database.models import Clone, User, CloneSettings
from NarzoxBots.services.encryption import encryption_service
from sqlalchemy import select
from sqlalchemy.orm import joinedload

class CloneManager:
    def __init__(self):
        self.clones = {} # bot_token: Client
        self.assistants = {} # bot_token: Client (Userbot)

    async def start_clone(self, bot_token: str, encrypted: bool = False, assistant_session: str = None):
        if encrypted:
            bot_token = encryption_service.decrypt(bot_token)

        if bot_token in self.clones:
            return self.clones[bot_token]

        client = Client(
            name=f"clone_{bot_token.split(':')[0]}",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=bot_token,
            plugins=dict(root="NarzoxBots.plugins")
        )

        try:
            await client.start()
            self.clones[bot_token] = client

            if assistant_session:
                # Start custom assistant for premium users
                assistant = Client(
                    name=f"assistant_{bot_token.split(':')[0]}",
                    api_id=config.API_ID,
                    api_hash=config.API_HASH,
                    session_string=assistant_session
                )
                await assistant.start()
                self.assistants[bot_token] = assistant
                logger.info(f"Started custom assistant for clone @{client.me.username}")

            logger.info(f"Started clone: @{client.me.username}")
            return client
        except Exception as e:
            logger.error(f"Failed to start clone with token {bot_token[:10]}...: {e}")
            return None

    async def stop_clone(self, bot_token: str):
        if bot_token in self.clones:
            client = self.clones.pop(bot_token)
            if client.is_connected:
                await client.stop()

            if bot_token in self.assistants:
                assistant = self.assistants.pop(bot_token)
                if assistant.is_connected:
                    await assistant.stop()

            logger.info(f"Stopped clone: @{client.me.username if client.me else 'Unknown'}")

    async def restart_clone(self, bot_token: str, assistant_session: str = None):
        await self.stop_clone(bot_token)
        return await self.start_clone(bot_token, assistant_session=assistant_session)

    async def load_all_clones(self):
        async with async_session() as session:
            result = await session.execute(
                select(Clone).where(Clone.status == "active").options(joinedload(Clone.settings))
            )
            clones = result.scalars().all()
            for clone in clones:
                assistant_session = clone.settings.assistant_session if clone.settings else None
                await self.start_clone(clone.bot_token, encrypted=True, assistant_session=assistant_session)

        asyncio.create_task(self.health_check())

    async def health_check(self):
        while True:
            await asyncio.sleep(300)
            for token, client in list(self.clones.items()):
                try:
                    if not client.is_connected:
                        await self.restart_clone(token)
                except:
                    pass

clone_manager = CloneManager()
