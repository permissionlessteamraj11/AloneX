from pyrogram import filters, Client
from pyrogram.types import Message
from NarzoxBots import app, config, db
from NarzoxBots.services.broadcast.service import run_global_broadcast
import asyncio

@Client.on_message(filters.command("broadcast") & filters.user(config.OWNER_ID))
async def global_broadcast_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to broadcast it.")

    await message.reply_text("Starting global broadcast...")
    await run_global_broadcast(message.reply_to_message, message.from_user.id)

@Client.on_message(filters.command("ownerbroadcast"))
async def owner_broadcast_cmd(client: Client, message: Message):
    # Logic for clone owners to broadcast only to their bot's users
    if client.me.id == app.me.id:
        return # Not for main bot

    user_id = message.from_user.id
    target_clone = None
    clones = await db.get_clones()
    for cid, cdata in clones.items():
        if cdata.get("bot_username") == client.me.username:
            target_clone = cdata
            break

    if not target_clone or target_clone.get("owner_id") != user_id:
        return await message.reply_text("You are not the owner of this clone.")

    # Logic to get users who started THIS specific bot token
    await message.reply_text("Owner broadcast feature coming soon...")
