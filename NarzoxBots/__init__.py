# Copyright (c) 2025 NarzoxBots
# Licensed under the MIT License.
# This file is part of NarzoxBotsMusic

from NarzoxBots.core.bot import Bot
from NarzoxBots.core.calls import TgCall
from NarzoxBots.core.dir import dir_setup
from NarzoxBots.core.mongo import MongoDB
from NarzoxBots.core.telegram import Telegram
from NarzoxBots.core.userbot import Userbot
from NarzoxBots.core.youtube import YouTube
from NarzoxBots.database.db import db_instance as db
from config import Config
import logging

# Setup Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("NarzoxBots")

# Load Config
config = Config()

# Initialize Core Components
dir_setup()
app = Bot()
userbot = Userbot()
anon = TgCall()
tg = Telegram()
yt = YouTube()

async def stop():
    """
    Asynchronously stops all bot components.
    """
    await app.exit()
    await userbot.exit()
    await anon.exit()
    # MongoDB close removed
    logger.info("All components stopped.")
