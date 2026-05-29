from pyrogram import filters, Client
from pyrogram.types import Message
from AloneX import app, config
from AloneX.services.broadcast.service import run_global_broadcast
from AloneX.database.db import async_session
from AloneX.database.models import User, Clone, Broadcast
from sqlalchemy import select
import asyncio

@Client.on_message(filters.command("broadcast") & filters.user(config.OWNER_ID))
async def global_broadcast_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to broadcast it.")

    query = message.reply_to_message.text
    await message.reply_text("Starting global broadcast...")
    await run_global_broadcast(query, message.from_user.id)

@Client.on_message(filters.command("ownerbroadcast"))
async def owner_broadcast_cmd(client: Client, message: Message):
    # Logic for clone owners to broadcast only to their bot's users
    if client.me.id == app.me.id:
        return # Not for main bot

    user_id = message.from_user.id
    async with async_session() as session:
        result = await session.execute(select(Clone).where(Clone.owner_id == user_id, Clone.bot_token == client.bot_token))
        clone = result.scalar_one_or_none()

        if not clone:
            return await message.reply_text("You are not the owner of this clone.")

        # Logic to get users who started THIS specific bot token
        # (Would need a way to track users per bot instance)
        await message.reply_text("Owner broadcast feature coming soon...")
