# Copyright (c) 2025 NarzoxBots
# ALONE-CODER

from pyrogram import Client, filters
from pyrogram.types import Message
from NarzoxBots import anon, queue, db, logger

@Client.on_message(filters.command("bass") & filters.group)
async def bass_boost(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /bass [level] (1-20)")

    level = message.command[1]
    if not level.isdigit() or not (1 <= int(level) <= 20):
        return await message.reply_text("Level must be between 1 and 20.")

    chat_id = message.chat.id
    if not await db.get_call(chat_id):
        return await message.reply_text("Nothing is playing.")

    media = queue.get_current(chat_id)
    if not media: return

    await message.reply_text(f"Applying bass boost level {level}... please wait.")
    await anon.play_media(chat_id, message, media, seek_time=media.time, bot_id=client.me.id, dsp={"bass": level})

@Client.on_message(filters.command("speed") & filters.group)
async def speed_control(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /speed [0.5-2.0]")

    try:
        speed = float(message.command[1])
        if not (0.5 <= speed <= 2.0): raise ValueError
    except:
        return await message.reply_text("Speed must be between 0.5 and 2.0.")

    chat_id = message.chat.id
    if not await db.get_call(chat_id):
        return await message.reply_text("Nothing is playing.")

    media = queue.get_current(chat_id)
    if not media: return

    await message.reply_text(f"Adjusting speed to {speed}x...")
    await anon.play_media(chat_id, message, media, seek_time=media.time, bot_id=client.me.id, dsp={"speed": speed})

@Client.on_message(filters.command("seek") & filters.group)
async def seek_hndlr(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /seek [seconds]")

    seconds = message.command[1]
    if not seconds.isdigit():
        return await message.reply_text("Seconds must be a number.")

    chat_id = message.chat.id
    if not await db.get_call(chat_id):
        return await message.reply_text("Nothing is playing.")

    media = queue.get_current(chat_id)
    if not media: return

    await message.reply_text(f"Seeking to {seconds} seconds...")
    await anon.play_media(chat_id, message, media, seek_time=int(seconds), bot_id=client.me.id)
