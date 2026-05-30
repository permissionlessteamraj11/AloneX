# Copyright (c) 2025 NarzoxBots
# Licensed under the MIT License.
# This file is part of NarzoxBotsMusic


import asyncio
import importlib

from pyrogram import idle

from NarzoxBots import (anon, app, config, db,
                   logger, stop, userbot, yt)
from NarzoxBots.database.db import init_db
from NarzoxBots.services.clones.manager import clone_manager
from NarzoxBots.plugins import all_modules


async def main():
    await db.connect()
    await init_db()
    await clone_manager.load_all_clones()
    await app.boot()
    await userbot.boot()
    await anon.boot()

    for module in all_modules:
        importlib.import_module(f"NarzoxBots.plugins.{module}")
    logger.info(f"Loaded {len(all_modules)} modules.")

    if config.COOKIES_URL:
        await yt.save_cookies(config.COOKIES_URL)

    sudoers = await db.get_sudoers()
    app.sudoers.update(sudoers)
    app.bl_users.update(await db.get_blacklisted())
    logger.info(f"Loaded {len(app.sudoers)} sudo users.")

    await idle()
    await stop()


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        pass
