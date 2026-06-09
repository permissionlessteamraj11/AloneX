# Copyright (c) 2025 NarzoxBots
# Licensed under the MIT License.

from pyrogram import Client, filters, types
from NarzoxBots import app, config, db, logger
import asyncio

@Client.on_message(filters.command("clonemcast") & filters.private)
async def clone_broadcast(client: Client, message: types.Message):
    is_clone = client.me.id != app.id
    if not is_clone:
        return # Main bot uses global broadcast

    user_id = message.from_user.id

    # Find clone ID and check ownership
    clone_id = None
    for cid, cdata in db.json_db.data["clones"].items():
        if cdata.get("bot_username") == client.me.username:
            clone_id = cid
            break

    if not clone_id or db.json_db.data["clones"][clone_id]["owner_id"] != user_id:
        return await message.reply_text("Unauthorized. Only the owner can broadcast.")

    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to broadcast it.")

    sent = await message.reply_text("Starting clone broadcast...")

    # In a real scenario, clones might track their own users.
    # For now, we broadcast to all users in the DB (simplification).
    # Ideally, we should filter by users who started this specific clone.
    users = list(db.json_db.data["users"].keys())

    count = 0
    for uid in users:
        try:
            await message.reply_to_message.copy(int(uid))
            count += 1
            await asyncio.sleep(0.1)
        except:
            pass

    await sent.edit_text(f"Broadcast completed. Sent to {count} users.")
