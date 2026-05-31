from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from NarzoxBots import app
from NarzoxBots.database.db import json_db

@Client.on_message(filters.command("settings") & filters.private)
async def settings_cmd(client: Client, message: Message):
    is_clone = client.me.id != app.me.id

    if is_clone:
        target_clone_id = None
        for cid, cdata in json_db.data["clones"].items():
            if cdata.get("bot_username") == client.me.username:
                target_clone_id = cid
                break

        if not target_clone_id:
            return

        clone_data = json_db.data["clones"][target_clone_id]
        if clone_data.get("owner_id") != message.from_user.id:
            return

        # Show settings menu for clone
        text = (
            f"Settings for @{client.me.username}\n\n"
            "Use commands to edit:\n"
            "/editwelcome - Change welcome text\n"
            "/editbuttons - Change buttons\n"
            "/setbio - Set assistant bio\n"
            "/setstart - Set start message\n"
            "/setfallback - Set fallback message\n"
            "/setsupport - Set support link\n"
            "/setfooter - Set custom footer\n"
            "/clonestats - View clone stats"
        )
        await message.reply_text(text)
    else:
        await message.reply_text("Main bot settings are managed via the Supreme Panel.")

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

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    is_clone = client.me.id != app.me.id

    if not is_clone:
        return await message.reply_text("Welcome to the Supreme Music Bot Platform!")

    target_clone_id = None
    for cid, cdata in json_db.data["clones"].items():
        if cdata.get("bot_username") == client.me.username:
            target_clone_id = cid
            break

    if target_clone_id:
        clone_data = json_db.data["clones"][target_clone_id]
        settings = json_db.data["clone_settings"].get(target_clone_id)

        welcome_text = "Welcome {first_name}!"
        if settings:
            welcome_text = settings.get("start_message") or settings.get("welcome_text") or welcome_text

        # Variable substitution
        welcome_text = welcome_text.format(
            first_name=message.from_user.first_name,
            username=message.from_user.username or "N/A",
            user_id=message.from_user.id,
            bot_name=client.me.first_name
        )

        # Attribution
        attribution = f"\n\n---\nPowered by Supreme Platform\nManaged by Owner ID: {clone_data.get('owner_id')}"

        keyboard = None
        if settings and settings.get("inline_buttons"):
            btn_list = []
            for btn in settings["inline_buttons"]:
                btn_list.append([InlineKeyboardButton(btn["text"], url=btn["url"])])
            keyboard = InlineKeyboardMarkup(btn_list)

        await message.reply_text(welcome_text + attribution, reply_markup=keyboard)
