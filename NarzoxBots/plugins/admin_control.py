# Copyright (c) 2025 NarzoxBots
# Licensed under the MIT License.

from pyrogram import Client, filters, types
from NarzoxBots import app, config, db
from NarzoxBots.helpers._permissions import permission

def get_toggle_markup(flags: dict, clone_id: str = None, user_id: int = None):
    buttons = []
    for flag, value in flags.items():
        status = "✅" if value else "❌"
        callback_data = f"toggle_flag {flag} {clone_id or 'global'}"
        buttons.append([types.InlineKeyboardButton(f"{flag.replace('_', ' ').upper()}: {status}", callback_data=callback_data)])

    if not clone_id and user_id == config.OWNER_ID:
        buttons.append([
            types.InlineKeyboardButton("📊 sᴛᴀᴛs", callback_data="admin_stats"),
            types.InlineKeyboardButton("⭐ ᴘʀᴇᴍɪᴜᴍ", callback_data="admin_premium")
        ])
        buttons.append([
            types.InlineKeyboardButton("📢 ʙʀᴏᴀᴅᴄᴀsᴛ", callback_data="admin_broadcast")
        ])
        buttons.append([types.InlineKeyboardButton("🌐 ᴡᴇʙ ᴅᴀsʜʙᴏᴀʀᴅ", url="https://narzoxbots.vercel.app")])

    buttons.append([types.InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="help close")])
    return types.InlineKeyboardMarkup(buttons)

@Client.on_message(filters.command("admin") & filters.private)
async def admin_panel(client: Client, message: types.Message):
    is_clone = client.me.id != app.id
    user_id = message.from_user.id

    clone_id = None
    if is_clone:
        for cid, cdata in db.json_db.data["clones"].items():
            if cdata.get("bot_username") == client.me.username:
                clone_id = cid
                break

        if not clone_id or (db.json_db.data["clones"][clone_id]["owner_id"] != user_id and user_id != config.OWNER_ID):
            return # Unauthorized
    else:
        if user_id != config.OWNER_ID:
            return # Unauthorized

    flags_to_show = ["music_enabled", "welcome_enabled", "maintenance_mode"]
    flags_data = {}
    for flag in flags_to_show:
        flags_data[flag] = await db.get_feature_flag(flag, clone_id)

    total_users = len(db.json_db.data["users"])
    total_chats = len(db.json_db.data["chats"])
    active_calls = len(db.active_calls)

    text = (
        "<b>ɴᴀʀᴢᴏx x ᴍᴜsɪᴄ ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ</b>\n\n"
        f"<b>ᴜsᴇʀs:</b> <code>{total_users}</code>\n"
        f"<b>ᴄʜᴀᴛs:</b> <code>{total_chats}</code>\n"
        f"<b>ᴀᴄᴛɪᴠᴇ sᴛʀᴇᴀᴍs:</b> <code>{active_calls}</code>\n\n"
        "ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ʙᴏᴛ ғᴇᴀᴛᴜʀᴇs ʀᴇᴀʟ-ᴛɪᴍᴇ."
    )
    await message.reply_text(text, reply_markup=get_toggle_markup(flags_data, clone_id, user_id))

@Client.on_callback_query(filters.regex("^toggle_flag"))
async def toggle_flag_cb(client: Client, query: types.CallbackQuery):
    parts = query.data.split()
    user_id = query.from_user.id

    if len(parts) == 3:
        _, flag, scope = parts
        clone_id = None if scope == "global" else scope
    else:
        _, flag = parts
        clone_id = None
        if client.me.id != app.id:
            for cid, cdata in db.json_db.data["clones"].items():
                if cdata.get("bot_username") == client.me.username:
                    clone_id = cid
                    break

    # Permission check
    if clone_id:
        clone_data = db.json_db.data["clones"].get(clone_id, {})
        if clone_data.get("owner_id") != user_id and user_id != config.OWNER_ID:
            return await query.answer("Unauthorized.", show_alert=True)
    else:
        if user_id != config.OWNER_ID:
            return await query.answer("Unauthorized.", show_alert=True)

    current_val = await db.get_feature_flag(flag, clone_id)
    new_val = not current_val
    await db.set_feature_flag(flag, new_val, clone_id)

    flags_to_show = ["music_enabled", "welcome_enabled", "maintenance_mode"]
    flags_data = {}
    for f in flags_to_show:
        flags_data[f] = await db.get_feature_flag(f, clone_id)

    await query.edit_message_reply_markup(reply_markup=get_toggle_markup(flags_data, clone_id, user_id))
    await query.answer(f"{flag.replace('_', ' ')} toggled to {'ON' if new_val else 'OFF'}")

@Client.on_callback_query(filters.regex("^admin_stats"))
async def admin_stats_cb(client: Client, query: types.CallbackQuery):
    if query.from_user.id != config.OWNER_ID:
        return await query.answer("Only Global Owner can view detailed stats.", show_alert=True)

    total_users = len(db.json_db.data["users"])
    total_chats = len(db.json_db.data["chats"])
    active_clones = len([c for c in db.json_db.data["clones"].values() if c.get("status") == "active"])
    premium_users = len([u for u in db.json_db.data["users"].values() if u.get("is_premium")])

    text = (
        "<b>📊 ᴅᴇᴛᴀɪʟᴇᴅ sᴛᴀᴛɪsᴛɪᴄs</b>\n\n"
        f"<b>ᴛᴏᴛᴀʟ ᴜsᴇʀs:</b> <code>{total_users}</code>\n"
        f"<b>ᴛᴏᴛᴀʟ ᴄʜᴀᴛs:</b> <code>{total_chats}</code>\n"
        f"<b>ᴀᴄᴛɪᴠᴇ ᴄʟᴏɴᴇs:</b> <code>{active_clones}</code>\n"
        f"<b>ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs:</b> <code>{premium_users}</code>\n"
        f"<b>ʀᴇᴠᴇɴᴜᴇ ᴇsᴛ:</b> <code>${premium_users * 10}</code>\n"
    )
    await query.edit_message_text(text, reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_back")]]))

@Client.on_callback_query(filters.regex("^admin_premium"))
async def admin_premium_cb(client: Client, query: types.CallbackQuery):
    if query.from_user.id != config.OWNER_ID:
        return await query.answer("Unauthorized.", show_alert=True)

    text = (
        "<b>⭐ ᴘʀᴇᴍɪᴜᴍ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n\n"
        "ᴛᴏ ɢʀᴀɴᴛ ᴘʀᴇᴍɪᴜᴍ, ᴜsᴇ:\n"
        "<code>/grant [user_id] [days]</code>\n\n"
        "ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴡɪᴛʜ <code>/grant [days]</code>"
    )
    await query.edit_message_text(text, reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_back")]]))

@Client.on_callback_query(filters.regex("^admin_broadcast"))
async def admin_broadcast_cb(client: Client, query: types.CallbackQuery):
    if query.from_user.id != config.OWNER_ID:
        return await query.answer("Unauthorized.", show_alert=True)

    text = (
        "<b>📢 ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏɴᴛʀᴏʟ</b>\n\n"
        "ᴜsᴇ <code>/broadcast</code> ʙʏ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ.\n\n"
        "<b>ᴏᴘᴛɪᴏɴs:</b>\n"
        "<code>-user</code> : ʙʀᴏᴀᴅᴄᴀsᴛ ᴛᴏ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛs\n"
        "<code>-nochat</code> : sᴋɪᴘ ɢʀᴏᴜᴘ ᴄʜᴀᴛs\n"
        "<code>-copy</code> : ᴄᴏᴘʏ ᴍᴇssᴀɢᴇ ɪɴsᴛᴇᴀᴅ ᴏғ ғᴏʀᴡᴀʀᴅ"
    )
    await query.edit_message_text(text, reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_back")]]))

@Client.on_callback_query(filters.regex("^admin_back"))
async def admin_back_cb(client: Client, query: types.CallbackQuery):
    await admin_panel(client, query.message)
    await query.message.delete()

@Client.on_message(filters.command("grant") & filters.user(config.OWNER_ID))
async def grant_premium_cmd(client: Client, message: types.Message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text("Usage: /grant [user_id] [days] or reply with /grant [days]")

    user_id = None
    days = 30

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        if len(message.command) >= 2:
            days = int(message.command[1])
    else:
        user_id = int(message.command[1])
        if len(message.command) >= 3:
            days = int(message.command[2])

    from datetime import datetime, timedelta, timezone
    expiry = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()

    if str(user_id) not in db.json_db.data["users"]:
        await db.add_user(user_id)

    db.json_db.data["users"][str(user_id)].update({"is_premium": True, "premium_expiry": expiry})
    await db.json_db._save()

    await message.reply_text(f"✅ ᴘʀᴇᴍɪᴜᴍ ɢʀᴀɴᴛᴇᴅ ᴛᴏ <code>{user_id}</code> ғᴏʀ {days} ᴅᴀʏs.")
