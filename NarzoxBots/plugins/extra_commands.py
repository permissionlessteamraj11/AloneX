from pyrogram import filters, Client
from pyrogram.types import Message
from NarzoxBots import app, config
from NarzoxBots.database.db import async_session
from NarzoxBots.database.models import User, Clone
from sqlalchemy import select
import datetime

@Client.on_message(filters.command("premium") & filters.private)
async def premium_status(client: Client, message: Message):
    user_id = message.from_user.id
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user and user.is_premium:
            expiry = user.premium_expiry or "Lifetime"
            await message.reply_text(f"You are a Premium User!\nExpiry: {expiry}")
        else:
            await message.reply_text("You are not a premium user. Contact @NarzoxUpdates to buy.")

@Client.on_message(filters.command("mybot") & filters.private)
async def my_bot_status(client: Client, message: Message):
    user_id = message.from_user.id
    async with async_session() as session:
        result = await session.execute(select(Clone).where(Clone.owner_id == user_id))
        clone = result.scalar_one_or_none()

        if clone:
            await message.reply_text(f"Your cloned bot: @{clone.bot_username}\nStatus: {clone.status}")
        else:
            await message.reply_text("You don't have any cloned bot.")

@Client.on_message(filters.command("status") & filters.user(config.OWNER_ID))
async def system_status(client: Client, message: Message):
    async with async_session() as session:
        # Simplified stats
        from sqlalchemy import func
        u_count = await session.execute(select(func.count(User.id)))
        c_count = await session.execute(select(func.count(Clone.id)))

        await message.reply_text(f"System Stats:\nTotal Users: {u_count.scalar()}\nActive Clones: {c_count.scalar()}")
