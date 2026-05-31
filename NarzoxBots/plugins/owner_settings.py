from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from NarzoxBots import app
from NarzoxBots.database.db import async_session
from NarzoxBots.database.models import Clone, CloneSettings
from sqlalchemy import select

@Client.on_message(filters.command("settings") & filters.private)
async def settings_cmd(client: Client, message: Message):
    # This should work on both main bot and clones
    # If on clone, check if user is owner
    is_clone = client.me.id != app.me.id

    async with async_session() as session:
        if is_clone:
            result = await session.execute(select(Clone).where(Clone.bot_token == client.bot_token))
            clone = result.scalar_one_or_none()
            if not clone or clone.owner_id != message.from_user.id:
                return # Only owner can use settings on clone

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

@Client.on_message(filters.command("editwelcome") & filters.private)
async def edit_welcome(client: Client, message: Message):
    if client.me.id == app.me.id: return

    if len(message.command) < 2:
        return await message.reply_text("Usage: /editwelcome [NEW_TEXT]")

    new_text = message.text.split(None, 1)[1]
    user_id = message.from_user.id

    async with async_session() as session:
        result = await session.execute(select(Clone).where(Clone.bot_token == client.bot_token))
        clone = result.scalar_one_or_none()

        if not clone or clone.owner_id != user_id:
            return await message.reply_text("Unauthorized.")

        result = await session.execute(select(CloneSettings).where(CloneSettings.clone_id == clone.id))
        settings = result.scalar_one_or_none()
        if settings:
            settings.welcome_text = new_text
            await session.commit()
            await message.reply_text("Welcome text updated!")

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

    user_id = message.from_user.id
    async with async_session() as session:
        result = await session.execute(select(Clone).where(Clone.bot_username == client.me.username))
        clone = result.scalar_one_or_none()
        if not clone or clone.owner_id != user_id: return

        result = await session.execute(select(CloneSettings).where(CloneSettings.clone_id == clone.id))
        settings = result.scalar_one_or_none()
        if settings:
            settings.inline_buttons = [{"text": label, "url": url}]
            await session.commit()
            await message.reply_text("Buttons updated!")

async def update_clone_setting(client, message, field, success_msg):
    if client.me.id == app.me.id: return
    if len(message.command) < 2:
        return await message.reply_text(f"Usage: /{message.command[0]} [VALUE]")

    value = message.text.split(None, 1)[1]
    user_id = message.from_user.id

    async with async_session() as session:
        result = await session.execute(select(Clone).where(Clone.bot_username == client.me.username))
        clone = result.scalar_one_or_none()
        if not clone or clone.owner_id != user_id:
            return await message.reply_text("Unauthorized.")

        result = await session.execute(select(CloneSettings).where(CloneSettings.clone_id == clone.id))
        settings = result.scalar_one_or_none()
        if settings:
            setattr(settings, field, value)
            await session.commit()
            await message.reply_text(success_msg)

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
    user_id = message.from_user.id

    async with async_session() as session:
        result = await session.execute(select(Clone).where(Clone.bot_username == client.me.username))
        clone = result.scalar_one_or_none()
        if not clone or clone.owner_id != user_id:
            return await message.reply_text("Unauthorized.")

        # In a real app, we would query bot-specific stats from MongoDB or Postgres
        # For now, let's provide a placeholder with basic info
        text = (
            f"📊 **Stats for @{client.me.username}**\n\n"
            f"Owner: `{clone.owner_id}`\n"
            f"Status: `{clone.status}`\n"
            f"Created At: `{clone.created_at.strftime('%Y-%m-%d %H:%M')}`\n"
        )
        await message.reply_text(text)

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    is_clone = client.me.id != app.me.id

    if not is_clone:
        return await message.reply_text("Welcome to the Supreme Music Bot Platform!")

    async with async_session() as session:
        result = await session.execute(select(Clone).where(Clone.bot_username == client.me.username))
        clone = result.scalar_one_or_none()

        if clone:
            result = await session.execute(select(CloneSettings).where(CloneSettings.clone_id == clone.id))
            settings = result.scalar_one_or_none()

            welcome_text = "Welcome {first_name}!"
            if settings:
                welcome_text = settings.start_message or settings.welcome_text or welcome_text

            # Variable substitution
            welcome_text = welcome_text.format(
                first_name=message.from_user.first_name,
                username=message.from_user.username or "N/A",
                user_id=message.from_user.id,
                bot_name=client.me.first_name
            )

            # Attribution
            attribution = f"\n\n---\nPowered by Supreme Platform\nManaged by Owner ID: {clone.owner_id}"

            keyboard = None
            if settings and settings.inline_buttons:
                btn_list = []
                for btn in settings.inline_buttons:
                    btn_list.append([InlineKeyboardButton(btn["text"], url=btn["url"])])
                keyboard = InlineKeyboardMarkup(btn_list)

            await message.reply_text(welcome_text + attribution, reply_markup=keyboard)
