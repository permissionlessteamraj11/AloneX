from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from NarzoxBots import app
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

@Client.on_message(filters.command("editwelcome") & filters.private)
async def edit_welcome(client: Client, message: Message):
    if client.me.id == app.me.id: return
    if len(message.command) < 2:
        return await message.reply_text("Usage: /editwelcome [NEW_TEXT]")

    new_text = message.text.split(None, 1)[1]
    clone_id, settings = await get_clone_and_settings(client.me.username, message.from_user.id)

    if settings:
        json_db.data["clone_settings"][clone_id]["welcome_text"] = new_text
        await json_db._save()
        await message.reply_text("Welcome text updated!")
    else:
        await message.reply_text("Unauthorized.")

@Client.on_message(filters.command("editbuttons") & filters.private)
async def edit_buttons(client: Client, message: Message):
    if client.me.id == app.me.id: return
    if len(message.command) < 2:
        return await message.reply_text("Usage: /editbuttons [BUTTON_LABEL] | [URL]")

    try:
        label, url = message.text.split(None, 1)[1].split("|")
        label = label.strip()
        url = url.strip()
    except:
        return await message.reply_text("Format: Label | URL")

    clone_id, settings = await get_clone_and_settings(client.me.username, message.from_user.id)
    if settings:
        json_db.data["clone_settings"][clone_id]["inline_buttons"] = [{"text": label, "url": url}]
        await json_db._save()
        await message.reply_text("Buttons updated!")
    else:
        await message.reply_text("Unauthorized.")

async def update_clone_setting(client, message, field, success_msg):
    if client.me.id == app.me.id: return
    if len(message.command) < 2:
        return await message.reply_text(f"Usage: /{message.command[0]} [VALUE]")

    value = message.text.split(None, 1)[1]
    clone_id, settings = await get_clone_and_settings(client.me.username, message.from_user.id)
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

