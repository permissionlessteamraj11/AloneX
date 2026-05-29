from pyrogram import filters, Client
from pyrogram.types import Message
from AloneX import app, db
from AloneX.services.clones.manager import clone_manager
from AloneX.services.encryption import encryption_service
from AloneX.database.db import async_session
from AloneX.database.models import Clone, User, CloneSettings
from sqlalchemy import select

@Client.on_message(filters.command("clone") & filters.private)
async def clone_bot(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /clone [BOT_TOKEN]")

    bot_token = message.text.split(None, 1)[1]
    user_id = message.from_user.id

    async with async_session() as session:
        # Check if user is premium
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_premium:
            return await message.reply_text("You need a premium subscription to clone a bot.")

        # Try to start the clone
        cloned_client = await clone_manager.start_clone(bot_token)
        if not cloned_client:
            return await message.reply_text("Invalid bot token or failed to start.")

        # Save to DB
        new_clone = Clone(
            owner_id=user_id,
            bot_token=encryption_service.encrypt(bot_token),
            bot_username=cloned_client.me.username,
            bot_name=cloned_client.me.first_name,
            status="active"
        )
        session.add(new_clone)
        await session.commit()

        # Initialize default settings
        settings = CloneSettings(clone_id=new_clone.id, welcome_text="Welcome to my music bot!")
        session.add(settings)
        await session.commit()

        await message.reply_text(f"Successfully cloned! Your bot is @{cloned_client.me.username}")

@Client.on_message(filters.command("removeclone") & filters.private)
async def remove_clone(client: Client, message: Message):
    user_id = message.from_user.id
    async with async_session() as session:
        result = await session.execute(select(Clone).where(Clone.owner_id == user_id))
        clone = result.scalar_one_or_none()
        if not clone:
            return await message.reply_text("You don't have an active clone.")

        await clone_manager.stop_clone(clone.bot_token)
        await session.delete(clone)
        await session.commit()
        await message.reply_text("Clone removed successfully.")
