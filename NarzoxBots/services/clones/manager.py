# Copyright (c) 2025 NarzoxBots
# ALONE-CODER

import asyncio
from pyrogram import Client, errors, filters
from NarzoxBots import config, logger, db
from NarzoxBots.services.encryption import encryption_service

class CloneManager:
    def __init__(self):
        self.clones = {} # bot_token: Client
        self.assistants = {} # bot_token: Client

    async def start_clone(self, bot_token: str, assistant_session: str = None):
        if bot_token in self.clones: return self.clones[bot_token]

        client = Client(
            name=f"clone_{bot_token.split(':')[0]}",
            api_id=config.API_ID, api_hash=config.API_HASH,
            bot_token=bot_token, plugins=dict(root="NarzoxBots.plugins")
        )
        try:
            await client.start()
            self.clones[bot_token] = client

            # Proactively cache the log group peer
            if config.LOGGER_ID:
                try:
                    await client.get_chat(config.LOGGER_ID)
                except errors.PeerIdInvalid:
                    logger.info(f"Clone @{client.me.username} could not access log group {config.LOGGER_ID}: Peer ID invalid. Please ensure the clone is a member of the log group.")
                except Exception as e:
                    logger.warning(f"Clone @{client.me.username} failed to access log group: {e}")

            if assistant_session:
                assistant = Client(
                    name=f"as_{bot_token.split(':')[0]}",
                    api_id=config.API_ID, api_hash=config.API_HASH,
                    session_string=assistant_session
                )
                await assistant.start()
                self.assistants[bot_token] = assistant

                # Proactively cache the log group peer for assistant
                if config.LOGGER_ID:
                    try:
                        await assistant.get_chat(config.LOGGER_ID)
                    except errors.PeerIdInvalid:
                        logger.info(f"Assistant for clone @{client.me.username} could not access log group {config.LOGGER_ID}: Peer ID invalid. Please ensure the assistant is a member of the log group.")
                    except:
                        pass

                # Register assistant with media system
                from NarzoxBots import anon
                await anon.register_assistant(client.me.id, assistant)

            from NarzoxBots.helpers import utils
            await utils.set_commands(client)

            logger.info(f"Started clone: @{client.me.username}")
            return client
        except Exception as e:
            logger.error(f"Failed to start clone: {e}")
            return None

    async def stop_clone(self, bot_token: str):
        client = self.clones.pop(bot_token, None)
        if client and client.is_connected:
            from NarzoxBots import anon
            await anon.unregister_assistant(client.me.id)
            await client.stop()

        assistant = self.assistants.pop(bot_token, None)
        if assistant and assistant.is_connected: await assistant.stop()

    async def load_all_clones(self):
        cursor = db.db.clones.find({"status": "active"})
        async for clone in cursor:
            token = encryption_service.decrypt(clone["bot_token"])
            await self.start_clone(token, assistant_session=clone.get("assistant_session"))

clone_manager = CloneManager()
