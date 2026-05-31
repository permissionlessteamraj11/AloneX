import asyncio
from pyrogram import Client, filters
from NarzoxBots import config, logger
from NarzoxBots.database.db import async_session
from NarzoxBots.database.models import Clone, User
from NarzoxBots.services.encryption import encryption_service
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
            plugins=dict(root="NarzoxBots.plugins") # Reuse existing plugins
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
            if client.is_connected:
                await client.stop()
            logger.info(f"Stopped clone: @{client.me.username}")

    async def restart_clone(self, bot_token: str):
        await self.stop_clone(bot_token)
        return await self.start_clone(bot_token)

    async def get_all_clones_status(self):
        status = {}
        for token, client in self.clones.items():
            status[token] = {
                "username": client.me.username if client.me else "Unknown",
                "is_connected": client.is_connected
            }
        return status

    async def load_all_clones(self):
        async with async_session() as session:
            result = await session.execute(select(Clone).where(Clone.status == "active"))
            clones = result.scalars().all()
            for clone in clones:
                await self.start_clone(clone.bot_token, encrypted=True)

        # Start health check task
        asyncio.create_task(self.health_check())

    async def health_check(self):
        while True:
            await asyncio.sleep(300) # Every 5 minutes
            logger.info("Running clones health check...")
            for token, client in list(self.clones.items()):
                try:
                    if not client.is_connected:
                        logger.warning(f"Clone @{client.me.username if client.me else 'Unknown'} is disconnected. Restarting...")
                        await self.restart_clone(token)
                except Exception as e:
                    logger.error(f"Error during health check for clone: {e}")

clone_manager = CloneManager()
