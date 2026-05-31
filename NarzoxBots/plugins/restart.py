# Copyright (c) 2025 NarzoxBots
# Licensed under the MIT License.
# This file is part of NarzoxBotsMusic
#ALONE-CODER

import os
import sys
import shutil
import asyncio

from pyrogram import Client, filters, types

from NarzoxBots import app, db, lang, stop


@Client.on_message(filters.command(["logs"]) & app.sudoers)
@lang.language()
async def _logs(client: Client, m: types.Message):
    sent = await m.reply_text(m.lang["log_fetch"])
    if not os.path.exists("log.txt"):
        return await sent.edit_text(m.lang["log_not_found"])

    await m.reply_document(
        document="log.txt",
        caption=m.lang["log_sent"].format(client.me.first_name),
    )
    await sent.delete()


@Client.on_message(filters.command(["logger"]) & app.sudoers)
@lang.language()
async def _logger(client: Client, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(m.lang["logger_usage"].format(m.command[0]))
    if m.command[1] not in ("on", "off"):
        return await m.reply_text(m.lang["logger_usage"].format(m.command[0]))

    if m.command[1] == "on":
        await db.set_logger(True)
        await m.reply_text(m.lang["logger_on"])
    else:
        await db.set_logger(False)
        await m.reply_text(m.lang["logger_off"])


@Client.on_message(filters.command(["restart"]) & app.sudoers)
@lang.language()
async def _restart(client: Client, m: types.Message):
    sent = await m.reply_text(m.lang["restarting"])

    for directory in ["cache", "downloads"]:
        shutil.rmtree(directory, ignore_errors=True)

    await sent.edit_text(m.lang["restarted"])
    asyncio.create_task(stop())
    await asyncio.sleep(2)

    try: os.remove("log.txt")
    except: pass

    os.execl(sys.executable, sys.executable, "-m", "NarzoxBots")
