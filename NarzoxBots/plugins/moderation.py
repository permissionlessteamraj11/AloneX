# Copyright (c) 2025 NarzoxBots
# Licensed under the MIT License.
# This file is part of NarzoxBotsMusic

import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message, ChatPrivileges, ChatPermissions
from NarzoxBots import app, db, config
from NarzoxBots.helpers._admins import admin_check

async def get_user_id(message: Message, text: str):
    if message.reply_to_message:
        return message.reply_to_message.from_user.id
    if len(text.split()) > 1:
        user = text.split()[1]
        if user.startswith("@"):
            try:
                user_obj = await app.get_users(user)
                return user_obj.id
            except:
                return None
        try:
            return int(user)
        except:
            return None
    return None

@Client.on_message(filters.command("kick") & filters.group)
@admin_check
async def kick_user(client: Client, message: Message):
    user_id = await get_user_id(message, message.text)
    if not user_id:
        return await message.reply_text("Reply to a user or provide username/ID.")
    try:
        await client.ban_chat_member(message.chat.id, user_id)
        await client.unban_chat_member(message.chat.id, user_id)
        await message.reply_text(f"Kicked user {user_id}")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@Client.on_message(filters.command("ban") & filters.group)
@admin_check
async def ban_user(client: Client, message: Message):
    user_id = await get_user_id(message, message.text)
    if not user_id:
        return await message.reply_text("Reply to a user or provide username/ID.")
    try:
        await client.ban_chat_member(message.chat.id, user_id)
        await message.reply_text(f"Banned user {user_id}")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@Client.on_message(filters.command("unban") & filters.group)
@admin_check
async def unban_user(client: Client, message: Message):
    user_id = await get_user_id(message, message.text)
    if not user_id:
        return await message.reply_text("Reply to a user or provide username/ID.")
    try:
        await client.unban_chat_member(message.chat.id, user_id)
        await message.reply_text(f"Unbanned user {user_id}")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@Client.on_message(filters.command("mute") & filters.group)
@admin_check
async def mute_user(client: Client, message: Message):
    user_id = await get_user_id(message, message.text)
    if not user_id:
        return await message.reply_text("Reply to a user or provide username/ID.")
    try:
        await client.restrict_chat_member(message.chat.id, user_id, permissions=ChatPermissions(can_send_messages=False))
        await message.reply_text(f"Muted user {user_id}")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@Client.on_message(filters.command("unmute") & filters.group)
@admin_check
async def unmute_user(client: Client, message: Message):
    user_id = await get_user_id(message, message.text)
    if not user_id:
        return await message.reply_text("Reply to a user or provide username/ID.")
    try:
        await client.restrict_chat_member(message.chat.id, user_id, permissions=ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        ))
        await message.reply_text(f"Unmuted user {user_id}")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@Client.on_message(filters.command("warn") & filters.group)
@admin_check
async def warn_user(client: Client, message: Message):
    user_id = await get_user_id(message, message.text)
    if not user_id:
        return await message.reply_text("Reply to a user or provide username/ID.")

    warns = await db.add_warn(message.chat.id, user_id)
    if warns >= 3:
        try:
            await client.restrict_chat_member(message.chat.id, user_id, permissions=ChatPermissions(can_send_messages=False))
            await db.reset_warns(message.chat.id, user_id)
            await message.reply_text(f"User {user_id} has been muted after 3 warnings.")
        except Exception as e:
            await message.reply_text(f"Error muting after warnings: {e}")
    else:
        await message.reply_text(f"Warned user {user_id}. Current warns: {warns}/3")

@Client.on_message(filters.command("warns") & filters.group)
@admin_check
async def view_warns(client: Client, message: Message):
    user_id = await get_user_id(message, message.text)
    if not user_id:
        user_id = message.from_user.id

    warns = await db.get_warns(message.chat.id, user_id)
    await message.reply_text(f"User {user_id} has {warns} warnings.")

@Client.on_message(filters.command("resetwarns") & filters.group)
@admin_check
async def reset_warns_hndlr(client: Client, message: Message):
    user_id = await get_user_id(message, message.text)
    if not user_id:
        return await message.reply_text("Reply to a user or provide username/ID.")

    await db.reset_warns(message.chat.id, user_id)
    await message.reply_text(f"Reset warnings for user {user_id}.")

@Client.on_message(filters.command("promote") & filters.group)
@admin_check
async def promote_user(client: Client, message: Message):
    user_id = await get_user_id(message, message.text)
    if not user_id:
        return await message.reply_text("Reply to a user or provide username/ID.")
    try:
        await client.promote_chat_member(
            message.chat.id,
            user_id,
            privileges=ChatPrivileges(
                can_change_info=True,
                can_delete_messages=True,
                can_restrict_members=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_promote_members=False,
                can_manage_video_chats=True
            )
        )
        await message.reply_text(f"Promoted user {user_id}")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@Client.on_message(filters.command("demote") & filters.group)
@admin_check
async def demote_user(client: Client, message: Message):
    user_id = await get_user_id(message, message.text)
    if not user_id:
        return await message.reply_text("Reply to a user or provide username/ID.")
    try:
        await client.promote_chat_member(
            message.chat.id,
            user_id,
            privileges=ChatPrivileges(
                can_change_info=False,
                can_delete_messages=False,
                can_restrict_members=False,
                can_invite_users=False,
                can_pin_messages=False,
                can_promote_members=False,
                can_manage_video_chats=False
            )
        )
        await message.reply_text(f"Demoted user {user_id}")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@Client.on_message(filters.command("tagall") & filters.group)
@admin_check
async def tag_all(client: Client, message: Message):
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else ""

    msg_id = message.id
    if message.reply_to_message:
        msg_id = message.reply_to_message.id

    members = []
    async for member in client.get_chat_members(message.chat.id):
        if not member.user.is_bot:
            members.append(member.user.mention)

    # Tag in chunks
    for i in range(0, len(members), 5):
        chunk = members[i:i+5]
        tag_text = f"{text}\n" + " ".join(chunk)
        await client.send_message(message.chat.id, tag_text, reply_to_message_id=msg_id)
        await asyncio.sleep(2)

@Client.on_message(filters.command("banall") & filters.group & filters.user(config.OWNER_ID))
async def ban_all(client: Client, message: Message):
    sent = await message.reply_text("Banning all members...")
    count = 0
    async for member in client.get_chat_members(message.chat.id):
        if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            try:
                await client.ban_chat_member(message.chat.id, member.user.id)
                count += 1
                if count % 10 == 0:
                    await sent.edit_text(f"Banning... {count} members banned.")
            except:
                pass
    await sent.edit_text(f"Completed. {count} members banned.")
