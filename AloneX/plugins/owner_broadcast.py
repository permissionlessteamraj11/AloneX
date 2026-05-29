from pyrogram import filters, Client
from pyrogram.types import Message
from AloneX import app
from AloneX.database.db import async_session
from AloneX.database.models import Clone, User
from AloneX.services.broadcast.service import BroadcastService
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
        asyncio.create_task(service.broadcast_to_users(0, user_ids, message.reply_to_message.text))
