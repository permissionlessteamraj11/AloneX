import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from NarzoxBots import app, config, yt, logger

@Client.on_message(filters.command("checkcookies") & filters.sudo)
async def check_cookies(client: Client, message: Message):
    cookie_dir = "NarzoxBots/cookies"
    if not os.path.exists(cookie_dir):
        return await message.reply_text("Cookie directory not found.")

    files = [f for f in os.listdir(cookie_dir) if f.endswith(".txt")]
    if not files:
        return await message.reply_text("No cookie files found.")

    report = "🍪 **Cookie Status Report**\n\n"
    for file in files:
        path = os.path.join(cookie_dir, file)
        size = os.path.getsize(path)
        mtime = os.path.getmtime(path)
        last_mod = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
        report += f"📄 `{file}`\n   - Size: `{size} bytes`\n   - Last Updated: `{last_mod}`\n\n"

    await message.reply_text(report)

@Client.on_message(filters.command("refreshcookies") & filters.sudo)
async def refresh_cookies(client: Client, message: Message):
    if not config.COOKIES_URL:
        return await message.reply_text("No COOKIES_URL configured in environment variables.")

    await message.reply_text("Refreshing cookies... please wait.")
    try:
        await yt.save_cookies(config.COOKIES_URL)
        await message.reply_text("Cookies refreshed successfully!")
    except Exception as e:
        logger.error(f"Refresh Cookies Error: {e}")
        await message.reply_text(f"Failed to refresh cookies: {e}")
