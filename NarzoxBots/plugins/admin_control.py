# Copyright (c) 2025 NarzoxBots
# ALONE-CODER

import psutil
import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from NarzoxBots import app, config, db, logger, boot
from NarzoxBots.helpers import utils

@Client.on_message(filters.command("admin") & app.sudoers)
async def admin_panel(client: Client, message: Message):
    if client.me.id != app.id: return

    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    uptime = utils.get_readable_time(int(time.time() - boot))

    total_users = await db.db.users.count_documents({})
    total_chats = await db.db.chats.count_documents({})
    active_clones = await db.db.clones.count_documents({"status": "active"})
    active_streams = len(db.active_calls)

    text = (
        "💎 **Narzox Professional Admin Panel**\n\n"
        f"🖥 **System Status:**\n"
        f"├ CPU: `{cpu}%` | RAM: `{ram}%`\n"
        f"└ Uptime: `{uptime}`\n\n"
        f"📊 **Bot Statistics:**\n"
        f"├ Users: `{total_users}` | Chats: `{total_chats}`\n"
        f"└ Clones: `{active_clones}` | Streams: `{active_streams}`\n"
    )

    buttons = [
        [
            InlineKeyboardButton("Add Sudo", callback_data="adm_add_sudo"),
            InlineKeyboardButton("Ban User", callback_data="adm_ban")
        ],
        [
            InlineKeyboardButton("Give Premium", callback_data="adm_give_prem"),
            InlineKeyboardButton("Stats", callback_data="admin_back")
        ],
        [InlineKeyboardButton("Close", callback_data="help close")]
    ]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("^adm_") & app.sudoers)
async def admin_actions(client: Client, cb: CallbackQuery):
    action = cb.data.split("_")[1]

    if action == "add_sudo":
        await cb.answer("Send the user ID to promote to sudo.", show_alert=True)
        # Logic for handling follow-up message would go here (using Conversation/ForceReply)
    elif action == "give_prem":
        await cb.answer("Send the user ID to grant lifetime premium.", show_alert=True)
    elif action == "ban":
        await cb.answer("Send the user ID/Chat ID to blacklist.", show_alert=True)

    await cb.answer(f"Action '{action}' initiated. Please use the corresponding command if needed.", show_alert=True)
