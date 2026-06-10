# Copyright (c) 2025 NarzoxBots
# ALONE-CODER

import asyncio
from pyrogram import idle
from NarzoxBots import (anon, app, config, db,
                   logger, stop, userbot, yt)
from NarzoxBots.services.clones.manager import clone_manager
import datetime

async def premium_check_service():
    """Background service to check and expire premium subscriptions."""
    while True:
        try:
            now = datetime.datetime.now(datetime.UTC)
            # Check users
            cursor = db.db.users.find({
                "is_premium": True,
                "premium_expiry": {"$lt": now},
                "premium_plan": {"$ne": "lifetime"}
            })
            async for user_data in cursor:
                user_id = user_data["_id"]
                await db.update_user(user_id, is_premium=False, premium_plan="none")
                logger.info(f"Premium expired for user {user_id}")
                try:
                    await app.send_message(user_id, "Your premium subscription has expired. Renew now to continue using premium features!")
                except: pass

            # Check Clones (if they have their own expiry)
            # Currently clones are tied to user premium, but we can add clone-specific expiry if needed.

        except Exception as e:
            logger.error(f"Error in premium_check_service: {e}")

        await asyncio.sleep(3600) # Check every hour

async def main():
    await db.connect()
    await clone_manager.load_all_clones()
    await app.boot()
    await userbot.boot()
    await anon.boot()

    if config.COOKIES_URL:
        await yt.save_cookies(config.COOKIES_URL)

    sudoers = await db.get_sudoers()
    app.sudoers.update(sudoers)
    app.bl_users.update(db.bl_users)
    logger.info(f"Loaded {len(app.sudoers)} sudo users.")

    # Start background services
    asyncio.create_task(premium_check_service())

    await idle()
    await stop()

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        pass
