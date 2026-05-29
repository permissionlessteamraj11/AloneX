from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from AloneX import app
from AloneX.database.db import async_session
from AloneX.database.models import Clone, CloneSettings
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
            text = f"Settings for @{client.me.username}\n\nUse commands to edit:\n/editwelcome - Change welcome text\n/editbuttons - Change buttons"
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
            welcome_text = settings.welcome_text if settings else "Welcome {first_name}!"

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
