from pyrogram import filters, Client
from pyrogram.types import Message
from NarzoxBots import app, db, config, logger
from NarzoxBots.services.clones.manager import clone_manager
from NarzoxBots.services.encryption import encryption_service
from NarzoxBots.database.db import async_session
from NarzoxBots.database.models import Clone, User, CloneSettings
from sqlalchemy import select

@Client.on_message(filters.command("clone") & filters.private)
async def clone_bot(client: Client, message: Message):
    try:
        if len(message.command) < 2:
            return await message.reply_text("Usage: /clone [BOT_TOKEN]")

        bot_token = message.text.split(None, 1)[1]
        user_id = message.from_user.id

        async with async_session() as session:
            # Check if user is premium
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if (not user or not user.is_premium) and user_id != config.OWNER_ID:
                return await message.reply_text("You need a premium subscription to clone a bot.")

            # Try to start the clone
            try:
                cloned_client = await clone_manager.start_clone(bot_token)
                if not cloned_client:
                    return await message.reply_text("Invalid bot token or failed to start.")
            except Exception as e:
                logger.error(f"Cloning Error: {e}")
                return await message.reply_text(f"Failed to clone bot: {str(e)}")

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
    except Exception as e:
        logger.error(f"Unexpected error in clone_bot: {e}")
        await message.reply_text("An unexpected error occurred during cloning.")

@Client.on_message(filters.command("removeclone") & filters.private)
async def remove_clone(client: Client, message: Message):
    try:
        user_id = message.from_user.id
        async with async_session() as session:
            result = await session.execute(select(Clone).where(Clone.owner_id == user_id))
            clone = result.scalar_one_or_none()
            if not clone:
                return await message.reply_text("You don't have an active clone.")

            try:
                await clone_manager.stop_clone(clone.bot_token)
            except Exception as e:
                logger.error(f"Error stopping clone: {e}")

            await session.delete(clone)
            await session.commit()
            await message.reply_text("Clone removed successfully.")
    except Exception as e:
        logger.error(f"Unexpected error in remove_clone: {e}")
        await message.reply_text("An unexpected error occurred while removing the clone.")
