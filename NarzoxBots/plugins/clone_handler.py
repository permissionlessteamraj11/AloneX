# Copyright (c) 2025 NarzoxBots
# ALONE-CODER

from pyrogram import filters, Client
from pyrogram.types import Message
from NarzoxBots import app, db, config, logger
from NarzoxBots.services.clones.manager import clone_manager
from NarzoxBots.services.encryption import encryption_service
from NarzoxBots.database.models import Clone, CloneSettings

@Client.on_message(filters.command("clone") & filters.private)
async def clone_bot(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /clone [BOT_TOKEN]")

    user = await db.get_user(message.from_user.id)
    if not (user and user.is_premium) and message.from_user.id != config.OWNER_ID:
        return await message.reply_text("Premium required to clone.")

    bot_token = message.text.split(None, 1)[1]
    sent = await message.reply_text("Starting your clone... please wait.")

    cloned_client = await clone_manager.start_clone(bot_token)
    if not cloned_client:
        return await sent.edit_text("Invalid token or failed to start.")

    clone_id = await db.db.clones.count_documents({}) + 1
    new_clone = Clone(
        id=clone_id, owner_id=message.from_user.id,
        bot_token=encryption_service.encrypt(bot_token),
        bot_username=cloned_client.me.username,
        bot_name=cloned_client.me.first_name
    )
    await db.db.clones.insert_one(new_clone.to_dict())

    settings = CloneSettings(id=clone_id, clone_id=clone_id)
    await db.db.clone_settings.insert_one(settings.to_dict())

    await sent.edit_text(f"Successfully cloned! @{cloned_client.me.username}")

@Client.on_message(filters.command("stopclone") & filters.private)
async def stop_clone(client: Client, message: Message):
    clone = await db.db.clones.find_one({"owner_id": message.from_user.id})
    if not clone: return await message.reply_text("No clone found.")

    token = encryption_service.decrypt(clone["bot_token"])
    await clone_manager.stop_clone(token)
    await db.db.clones.update_one({"_id": clone["_id"]}, {"$set": {"status": "stopped"}})
    await message.reply_text("Clone stopped.")
