from pyrogram import filters, Client
from pyrogram.types import Message
from NarzoxBots import app, db, config, logger
from NarzoxBots.services.clones.manager import clone_manager
from NarzoxBots.services.encryption import encryption_service
from NarzoxBots.database.db import json_db
from NarzoxBots.database.models import Clone, User, CloneSettings

@Client.on_message(filters.command("clone") & filters.private)
async def clone_bot(client: Client, message: Message):
    try:
        if len(message.command) < 2:
            return await message.reply_text("Usage: /clone [BOT_TOKEN]")

        bot_token = message.text.split(None, 1)[1]
        user_id = message.from_user.id

        user_data = json_db.data["users"].get(str(user_id))
        is_premium = user_data.get("is_premium") if user_data else False

        if not is_premium and user_id != config.OWNER_ID:
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
        clone_id = str(len(json_db.data["clones"]) + 1)
        new_clone = Clone(
            id=int(clone_id),
            owner_id=user_id,
            bot_token=encryption_service.encrypt(bot_token),
            bot_username=cloned_client.me.username,
            bot_name=cloned_client.me.first_name,
            status="active"
        )
        json_db.data["clones"][clone_id] = new_clone.to_dict()

        # Initialize default settings
        settings = CloneSettings(id=int(clone_id), clone_id=int(clone_id), welcome_text="Welcome to my music bot!")
        json_db.data["clone_settings"][clone_id] = settings.to_dict()

        await json_db._save()

        await message.reply_text(f"Successfully cloned! Your bot is @{cloned_client.me.username}")
    except Exception as e:
        logger.error(f"Unexpected error in clone_bot: {e}")
        await message.reply_text("An unexpected error occurred during cloning.")

@Client.on_message(filters.command("removeclone") & filters.private)
async def remove_clone(client: Client, message: Message):
    try:
        user_id = message.from_user.id
        target_clone_id = None
        for cid, cdata in json_db.data["clones"].items():
            if cdata.get("owner_id") == user_id:
                target_clone_id = cid
                break

        if not target_clone_id:
            return await message.reply_text("You don't have an active clone.")

        clone_data = json_db.data["clones"][target_clone_id]
        try:
            await clone_manager.stop_clone(clone_data.get("bot_token"))
        except Exception as e:
            logger.error(f"Error stopping clone: {e}")

        del json_db.data["clones"][target_clone_id]
        if target_clone_id in json_db.data["clone_settings"]:
            del json_db.data["clone_settings"][target_clone_id]

        await json_db._save()
        await message.reply_text("Clone removed successfully.")
    except Exception as e:
        logger.error(f"Unexpected error in remove_clone: {e}")
        await message.reply_text("An unexpected error occurred while removing the clone.")
