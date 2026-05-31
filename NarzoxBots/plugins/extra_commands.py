from pyrogram import filters, Client
from pyrogram.types import Message
from NarzoxBots import app, config
from NarzoxBots.database.db import json_db
import datetime

@Client.on_message(filters.command("premium") & filters.private)
async def premium_status(client: Client, message: Message):
    user_id = message.from_user.id
    user_data = json_db.data["users"].get(str(user_id))

    if user_data and user_data.get("is_premium"):
        expiry = user_data.get("premium_expiry") or "Lifetime"
        await message.reply_text(f"You are a Premium User!\nExpiry: {expiry}")
    else:
        await message.reply_text("You are not a premium user. Contact @NarzoxUpdates to buy.")

@Client.on_message(filters.command("mybot") & filters.private)
async def my_bot_status(client: Client, message: Message):
    user_id = message.from_user.id
    target_clone = None
    for cid, cdata in json_db.data["clones"].items():
        if cdata.get("owner_id") == user_id:
            target_clone = cdata
            break

    if target_clone:
        await message.reply_text(f"Your cloned bot: @{target_clone.get('bot_username')}\nStatus: {target_clone.get('status')}")
    else:
        await message.reply_text("You don't have any cloned bot.")

@Client.on_message(filters.command("status") & filters.user(config.OWNER_ID))
async def system_status(client: Client, message: Message):
    u_count = len(json_db.data["users"])
    c_count = len(json_db.data["clones"])
    await message.reply_text(f"System Stats:\nTotal Users: {u_count}\nActive Clones: {c_count}")
