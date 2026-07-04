# Copyright (c) 2025 NarzoxBots
# ALONE-CODER

from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from NarzoxBots import app, config, db, logger
from NarzoxBots.services.clones.manager import clone_manager
from NarzoxBots.services.encryption import encryption_service

async def is_clone_owner(client, user_id):
    if user_id == config.OWNER_ID: return True
    data = await db.db.clones.find_one({"bot_username": client.me.username, "owner_id": user_id})
    return data is not None

@Client.on_message(filters.command(["config", "settings"]) & filters.private)
async def clone_settings(client: Client, message: Message):
    if client.me.id == app.id: return
    if not await is_clone_owner(client, message.from_user.id):
        return await message.reply_text("Unauthorized.")

    clone_data = await db.db.clones.find_one({"bot_username": client.me.username})
    settings = await db.db.clone_settings.find_one({"_id": clone_data["_id"]})

    text = (
        f"🛠 **Clone Configuration: @{client.me.username}**\n\n"
        f"**Welcome Text:** {settings.get('welcome_text')}\n"
        f"**Music:** {'✅' if settings.get('music_enabled') else '❌'}\n"
        f"**Maintenance:** {'✅' if settings.get('maintenance_mode') else '❌'}\n"
        f"**Assistant:** {'✅ Set' if clone_data.get('assistant_session') else '❌ Not Set'}\n"
    )

    buttons = [
        [
            InlineKeyboardButton("Set Assistant", callback_data="clone_as_set"),
            InlineKeyboardButton("Remove Assistant", callback_data="clone_as_rm")
        ],
        [
            InlineKeyboardButton("Toggle Music", callback_data="toggle_clone music_enabled"),
            InlineKeyboardButton("Toggle Maint", callback_data="toggle_clone maintenance_mode")
        ],
        [InlineKeyboardButton("Close", callback_data="help close")]
    ]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("^clone_as_") & filters.private)
async def clone_assistant_cb(client: Client, cb: CallbackQuery):
    if not await is_clone_owner(client, cb.from_user.id): return

    action = cb.data.split("_")[2]
    clone_data = await db.db.clones.find_one({"bot_username": client.me.username})

    if action == "set":
        await cb.answer("Send /setassistant [SESSION] to login your custom assistant.", show_alert=True)
    elif action == "rm":
        await db.db.clones.update_one({"_id": clone_data["_id"]}, {"$unset": {"assistant_session": ""}})
        token = encryption_service.decrypt(clone_data["bot_token"])
        await clone_manager.stop_clone(token)
        await clone_manager.start_clone(token)
        await cb.answer("Assistant removed and clone restarted.")
        return await clone_settings(client, cb.message)
