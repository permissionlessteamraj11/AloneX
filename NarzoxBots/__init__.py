# Copyright (c) 2025 NarzoxBots
# Licensed under the MIT License.
# This file is part of NarzoxBotsMusic

import logging
from config import Config

# Setup Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("NarzoxBots")

# Load Config
config = Config()

# Initialize Database
from NarzoxBots.database.db import db_instance as db

# Initialize Language
from NarzoxBots.core.lang import Language
lang = Language()

# Initialize Core Components
from NarzoxBots.core.dir import ensure_dirs
ensure_dirs()

from NarzoxBots.core.bot import Bot
app = Bot()

from NarzoxBots.core.userbot import Userbot
userbot = Userbot()

from NarzoxBots.core.youtube import YouTube
yt = YouTube()

from NarzoxBots.core.telegram import Telegram
tg = Telegram()

# Initialize Queue
from NarzoxBots.helpers._queue import Queue
queue = Queue()

# TgCall depends on app, config, db, lang, logger, queue, userbot, yt
from NarzoxBots.core.calls import TgCall
anon = TgCall()

async def stop():
    """
    Asynchronously stops all bot components.
    """
    await app.exit()
    await userbot.exit()
    await anon.exit()
    logger.info("All components stopped.")
