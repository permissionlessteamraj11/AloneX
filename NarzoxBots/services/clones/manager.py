import asyncio
from pyrogram import Client, filters
from NarzoxBots import config, logger
from NarzoxBots.database.db import json_db
from NarzoxBots.services.encryption import encryption_service

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
        # Custom attribute for easier tracking
        client.bot_token = bot_token

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
        for cid, clone_data in json_db.data["clones"].items():
            if clone_data.get("status") == "active":
                settings = json_db.data["clone_settings"].get(cid)
                assistant_session = settings.get("assistant_session") if settings else None
                await self.start_clone(clone_data.get("bot_token"), encrypted=True, assistant_session=assistant_session)

        asyncio.create_task(self.health_check())

    async def health_check(self):
        while True:
            await asyncio.sleep(300)
            for token, client in list(self.clones.items()):
                try:
                    if not client.is_connected:
                        # Find assistant session from settings
                        assistant_session = None
                        for cid, cdata in json_db.data["clones"].items():
                            if cdata.get("bot_token") == token:
                                settings = json_db.data["clone_settings"].get(cid)
                                if settings:
                                    assistant_session = settings.get("assistant_session")
                                break
                        await self.restart_clone(token, assistant_session=assistant_session)
                except:
                    pass

clone_manager = CloneManager()
