from pyrogram import filters, Client
from pyrogram.types import Message
from NarzoxBots import app, config
from NarzoxBots.database.db import async_session
from NarzoxBots.database.models import Clone, User
from NarzoxBots.services.broadcast.service import BroadcastService
from sqlalchemy import select
import asyncio

@Client.on_message(filters.command("ownerbroadcast") & filters.private)
async def owner_broadcast_handler(client: Client, message: Message):
    if client.me.id == app.me.id:
        return await message.reply_text("This command only works on your cloned bot.")

    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to broadcast.")

    user_id = message.from_user.id
    async with async_session() as session:
        # Verify ownership
        result = await session.execute(select(Clone).where(Clone.owner_id == user_id, Clone.bot_username == client.me.username))
        clone = result.scalar_one_or_none()

        if not clone:
            return await message.reply_text("You don't own this bot instance.")

        # For simplicity, we broadcast to all known users in the DB
        # Ideally, we should filter users who have interacted with this specific clone
        result = await session.execute(select(User.id))
        user_ids = [r[0] for r in result.all()]

        await message.reply_text(f"Starting broadcast to {len(user_ids)} users...")
        service = BroadcastService(client)
        # We don't track owner broadcasts in the main Broadcast table for now to avoid clutter
        asyncio.create_task(service.broadcast_to_users(0, user_ids, message.reply_to_message))


@Client.on_message(filters.command("globalbroadcast") & filters.user(config.OWNER_ID))
async def global_broadcast_handler(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to global broadcast.")

    from NarzoxBots.services.clones.manager import clone_manager
    from NarzoxBots.services.broadcast.service import BroadcastService
    from NarzoxBots.database.db import async_session
    from NarzoxBots.database.models import User
    from sqlalchemy import select

    async with async_session() as session:
        result = await session.execute(select(User.id))
        user_ids = [r[0] for r in result.all()]

    if not user_ids:
        return await message.reply_text("No users found in database.")

    await message.reply_text(f"Starting global broadcast through {len(clone_manager.clones) + 1} bots to {len(user_ids)} users...")

    # Broadcast via main bot
    service_main = BroadcastService(app)
    asyncio.create_task(service_main.broadcast_to_users(0, user_ids, message.reply_to_message))

    # Broadcast via each clone
    for token, clone_client in clone_manager.clones.items():
        if not clone_client.is_connected:
            continue
        service_clone = BroadcastService(clone_client)
        asyncio.create_task(service_clone.broadcast_to_users(0, user_ids, message.reply_to_message))

    await message.reply_text("Global broadcast tasks initiated for all bot instances.")
