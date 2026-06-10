# Copyright (c) 2025 NarzoxBots
# Licensed under the MIT License.
# This file is part of NarzoxBotsMusic
# ALONE-CODER

import asyncio
from pyrogram import enums, filters, types, Client

from NarzoxBots import app, config, db, lang
from NarzoxBots.helpers import buttons, utils

@Client.on_message(filters.command(["help"]) & filters.private & ~app.bl_users)
@lang.language()
async def _help(client: Client, m: types.Message):
    await m.reply_text(
        text=m.lang["help_menu"],
        reply_markup=buttons.help_markup(m.lang),
        quote=True,
    )


@Client.on_message(filters.command(["start"]))
@lang.language()
async def start(client: Client, message: types.Message):
    # Ensure only the targeted bot responds in groups
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        if "@" in message.text.split()[0] and not message.text.split()[0].endswith(client.me.username):
            return

        if client.me.id != app.id and "@" not in message.text.split()[0]:
            try:
                await client.get_chat_member(message.chat.id, app.id)
                return # Main bot present
            except:
                pass

    is_clone = client.me.id != app.id
    clone_id = None
    if is_clone:
        clones = await db.get_clones()
        for cid, cdata in clones.items():
            if cdata.get("bot_username") == client.me.username:
                clone_id = cid
                break

    if not await db.get_feature_flag("welcome_enabled", clone_id):
        if not await db.get_feature_flag("maintenance_mode", clone_id):
             return # Silently ignore if disabled

    if message.from_user.id in app.bl_users and message.from_user.id not in db.notified:
        return await message.reply_text(message.lang["bl_user_notify"])

    if len(message.command) > 1 and message.command[1] == "help":
        return await _help(client, message)

    private = message.chat.type == enums.ChatType.PRIVATE

    # Check if it's a clone
    is_clone = client.me.id != app.id

    start_img = config.START_IMG
    support_link = config.SUPPORT_CHAT
    updates_link = config.SUPPORT_CHANNEL
    group_link = None
    owner_link = "https://t.me/zolvid"
    clone_link = f"https://t.me/{app.username}"

    if is_clone:
        target_clone_id = None
        clones = await db.get_clones()
        for cid, cdata in clones.items():
            if cdata.get("bot_username") == client.me.username:
                target_clone_id = cid
                break

        if target_clone_id:
            settings = await db.get_settings(target_clone_id)
            if settings:
                start_img = settings.welcome_media or start_img
                support_link = settings.support_link or support_link
                updates_link = settings.updates_link or updates_link
                group_link = settings.group_link
                owner_link = settings.owner_link or owner_link
                clone_link = settings.clone_link or clone_link
    else:
        settings = await db.get_settings()
        if settings:
            start_img = settings.welcome_banner or start_img
            support_link = settings.support_link or support_link
            updates_link = settings.updates_link or updates_link
            owner_link = settings.owner_link or owner_link

    if private:
        user_mention = message.from_user.mention
        _text = message.lang["start_pm"].format(user_mention)
    else:
        _text = message.lang["start_gp"]

    key = buttons.start_key(
        message.lang,
        private,
        bot_username=client.me.username,
        support=support_link,
        updates=updates_link,
        owner=owner_link,
        clone=clone_link,
        group=group_link
    )

    # Check if already welcomed (once per user flow)
    user_data = await db.get_user(message.from_user.id)
    if private and user_data and user_data.welcomed:
        # Still send the message but maybe keep it logged or track sessions
        pass

    if start_img:
        await message.reply_photo(
            photo=start_img,
            caption=_text,
            reply_markup=key,
            quote=not private,
        )
    else:
        await message.reply_text(
            text=_text,
            reply_markup=key,
            quote=not private,
        )

    if private:
        if user_data:
            if not user_data.welcomed:
                await db.update_user(message.from_user.id, welcomed=True)
            return
        await utils.send_log(message)
        await db.add_user(message.from_user.id, welcomed=True)
    else:
        if await db.is_chat(message.chat.id):
            return
        await utils.send_log(message, True)
        await db.add_chat(message.chat.id)


@Client.on_message(filters.command(["playmode", "settings"]) & filters.group & ~app.bl_users)
@lang.language()
async def settings(client: Client, message: types.Message):
    admin_only = await db.get_play_mode(message.chat.id)
    cmd_delete = await db.get_cmd_delete(message.chat.id)
    _language = await db.get_lang(message.chat.id)
    await message.reply_text(
        text=message.lang["start_settings"].format(message.chat.title),
        reply_markup=buttons.settings_markup(
            message.lang, admin_only, cmd_delete, _language, message.chat.id
        ),
        quote=True,
    )


@Client.on_message(filters.new_chat_members, group=7)
@lang.language()
async def _new_member(client: Client, message: types.Message):
    if message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.chat.leave()

    await asyncio.sleep(3)
    for member in message.new_chat_members:
        if member.id == client.me.id:
            if await db.is_chat(message.chat.id):
                return
            await utils.send_log(message, True)
            await db.add_chat(message.chat.id)
