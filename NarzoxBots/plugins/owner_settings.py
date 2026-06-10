from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from NarzoxBots import app, config
from NarzoxBots.database.db import json_db


async def get_clone_and_settings(client_username, user_id):
    target_clone_id = None
    for cid, cdata in json_db.data["clones"].items():
        if cdata.get("bot_username") == client_username:
            target_clone_id = cid
            break

    if not target_clone_id:
        return None, None

    clone_data = json_db.data["clones"][target_clone_id]
    if clone_data.get("owner_id") != user_id:
        return None, None

    settings_data = json_db.data["clone_settings"].get(target_clone_id)
    return target_clone_id, settings_data

async def has_permission(client, user_id):
    user_data = json_db.data["users"].get(str(user_id))
    is_premium = user_data.get("is_premium") if user_data else False
    if is_premium or user_id == config.OWNER_ID:
        return True

    clone_id, settings = await get_clone_and_settings(client.me.username, user_id)
    return clone_id is not None

@Client.on_message(filters.command("editwelcome") & filters.private)
async def edit_welcome(client: Client, message: Message):
    if client.me.id == app.me.id: return
    user_id = message.from_user.id

    if not await has_permission(client, user_id):
        return await message.reply_text("This is a premium feature. Please upgrade to use it.")

    if len(message.command) < 2:
        return await message.reply_text("Usage: /editwelcome [NEW_TEXT]")

    new_text = message.text.split(None, 1)[1]
    clone_id, settings = await get_clone_and_settings(client.me.username, user_id)

    if settings:
        json_db.data["clone_settings"][clone_id]["welcome_text"] = new_text
        await json_db._save()
        await message.reply_text("Welcome text updated!")
    else:
        await message.reply_text("Unauthorized.")

@Client.on_message(filters.command("editbuttons") & filters.private)
async def edit_buttons(client: Client, message: Message):
    if client.me.id == app.me.id: return
    user_id = message.from_user.id

    if not await has_permission(client, user_id):
        return await message.reply_text("This is a premium feature. Please upgrade to use it.")

    if len(message.command) < 2:
        return await message.reply_text("Usage: /editbuttons [BUTTON_LABEL] | [URL]")

    try:
        label, url = message.text.split(None, 1)[1].split("|")
        label = label.strip()
        url = url.strip()
    except:
        return await message.reply_text("Format: Label | URL")

    clone_id, settings = await get_clone_and_settings(client.me.username, user_id)
    if settings:
        json_db.data["clone_settings"][clone_id]["inline_buttons"] = [{"text": label, "url": url}]
        await json_db._save()
        await message.reply_text("Buttons updated!")
    else:
        await message.reply_text("Unauthorized.")

async def update_clone_setting(client, message, field, success_msg):
    if client.me.id == app.me.id: return
    user_id = message.from_user.id

    if not await has_permission(client, user_id):
        return await message.reply_text("This is a premium feature. Please upgrade to use it.")

    if len(message.command) < 2:
        return await message.reply_text(f"Usage: /{message.command[0]} [VALUE]")

    value = message.text.split(None, 1)[1]
    clone_id, settings = await get_clone_and_settings(client.me.username, user_id)
    if settings:
        json_db.data["clone_settings"][clone_id][field] = value
        await json_db._save()
        await message.reply_text(success_msg)
    else:
        await message.reply_text("Unauthorized.")

@Client.on_message(filters.command("setbio") & filters.private)
async def set_bio(client: Client, message: Message):
    await update_clone_setting(client, message, "assistant_bio", "Assistant bio updated!")

@Client.on_message(filters.command("setstart") & filters.private)
async def set_start(client: Client, message: Message):
    await update_clone_setting(client, message, "start_message", "Start message updated!")

@Client.on_message(filters.command("setfallback") & filters.private)
async def set_fallback(client: Client, message: Message):
    await update_clone_setting(client, message, "fallback_message", "Fallback message updated!")

@Client.on_message(filters.command("setsupport") & filters.private)
async def set_support(client: Client, message: Message):
    await update_clone_setting(client, message, "support_link", "Support link updated!")

@Client.on_message(filters.command("setfooter") & filters.private)
async def set_footer(client: Client, message: Message):
    await update_clone_setting(client, message, "custom_footer", "Custom footer updated!")

@Client.on_message(filters.command("setupdates") & filters.private)
async def set_updates(client: Client, message: Message):
    await update_clone_setting(client, message, "updates_link", "Updates link updated!")

@Client.on_message(filters.command("setgroup") & filters.private)
async def set_group(client: Client, message: Message):
    await update_clone_setting(client, message, "group_link", "Group link updated!")

@Client.on_message(filters.command("setassistant") & filters.private)
async def set_assistant_session(client: Client, message: Message):
    if client.me.id == app.me.id: return
    user_id = message.from_user.id

    if not await has_permission(client, user_id):
        return await message.reply_text("This is a premium feature. Please upgrade to use it.")

    if len(message.command) < 2:
        return await message.reply_text("Usage: /setassistant [SESSION_STRING]")

    session = message.text.split(None, 1)[1]
    clone_id, settings = await get_clone_and_settings(client.me.username, user_id)
    if settings:
        json_db.data["clone_settings"][clone_id]["assistant_session"] = session
        await json_db._save()
        await message.reply_text("Assistant session updated! Restarting clone to apply changes...")
        clone_data = json_db.data["clones"][clone_id]
        from NarzoxBots.services.clones.manager import clone_manager
        await clone_manager.restart_clone(clone_data.get("bot_token"), assistant_session=session)
    else:
        await message.reply_text("Unauthorized.")

@Client.on_message(filters.command(["config", "botsettings"]) & filters.private)
async def bot_config(client: Client, message: Message):
    if client.me.id == app.me.id: return
    clone_id, settings = await get_clone_and_settings(client.me.username, message.from_user.id)

    if not settings:
        return await message.reply_text("Unauthorized.")

    text = (
        f"🛠 **Bot Configuration: @{client.me.username}**\n\n"
        f"**Welcome Text:** {settings.get('welcome_text')}\n"
        f"**Support:** {settings.get('support_link')}\n"
        f"**Updates:** {settings.get('updates_link')}\n"
        f"**Assistant:** {'Set' if settings.get('assistant_session') else 'Not Set'}\n\n"
        f"**Music Enabled:** {'✅' if settings.get('music_enabled', True) else '❌'}\n"
        f"**Welcome Enabled:** {'✅' if settings.get('welcome_enabled', True) else '❌'}\n"
        f"**Maintenance:** {'✅' if settings.get('maintenance_mode', False) else '❌'}\n"
    )

    buttons = [
        [
            InlineKeyboardButton("Edit Welcome", callback_data="edit_welcome_config"),
            InlineKeyboardButton("Edit Support", callback_data="edit_support_config")
        ],
        [
            InlineKeyboardButton("Edit Updates", callback_data="edit_updates_config"),
            InlineKeyboardButton("Edit Group", callback_data="edit_group_config")
        ],
        [
            InlineKeyboardButton("Assistant", callback_data="edit_assistant_config")
        ],
        [
            InlineKeyboardButton("Music", callback_data="toggle_flag music_enabled"),
            InlineKeyboardButton("Welcome", callback_data="toggle_flag welcome_enabled"),
            InlineKeyboardButton("Maintenance", callback_data="toggle_flag maintenance_mode")
        ],
        [InlineKeyboardButton("Close", callback_data="help close")]
    ]

    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_message(filters.command("clonestats") & filters.private)
async def clone_stats(client: Client, message: Message):
    if client.me.id == app.me.id: return
    clone_id, settings = await get_clone_and_settings(client.me.username, message.from_user.id)

    if clone_id:
        clone_data = json_db.data["clones"][clone_id]
        text = (
            f"📊 **Stats for @{client.me.username}**\n\n"
            f"Owner: `{clone_data.get('owner_id')}`\n"
            f"Status: `{clone_data.get('status')}`\n"
            f"Created At: `{clone_data.get('created_at')}`\n"
        )
        await message.reply_text(text)
    else:
        await message.reply_text("Unauthorized.")
