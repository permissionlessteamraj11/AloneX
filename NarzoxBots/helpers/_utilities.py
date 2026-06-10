# Copyright (c) 2025 NarzoxBots
# Licensed under the MIT License.
# This file is part of NarzoxBotsMusic
#ALONE-CODER

import re

from pyrogram import enums, types

from NarzoxBots import app, config


class Utilities:
    def __init__(self):
        pass

    def format_eta(self, seconds: int) -> str:
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}:{seconds % 60:02d} min"
        else:
            h = seconds // 3600
            m = (seconds % 3600) // 60
            s = seconds % 60
            return f"{h}:{m:02d}:{s:02d} h"

    def format_size(self, bytes: int) -> str:
        if bytes >= 1024**3:
            return f"{bytes / 1024 ** 3:.2f} GB"
        elif bytes >= 1024**2:
            return f"{bytes / 1024 ** 2:.2f} MB"
        else:
            return f"{bytes / 1024:.2f} KB"

    def to_seconds(self, time: str) -> int:
        parts = [int(p) for p in time.strip().split(":")]
        return sum(value * 60**i for i, value in enumerate(reversed(parts)))


    def get_url(self, message_1: types.Message) -> str | None:
        link = None
        messages = [message_1]
        entities = [enums.MessageEntityType.URL, enums.MessageEntityType.TEXT_LINK]

        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)

        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type in entities:
                        link = entity.url
                        break

            if message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type in entities:
                        link = entity.url
                        break

        if link:
            return link.split("&si")[0].split("?si")[0]
        return None


    async def extract_user(self, msg: types.Message) -> types.User | None:
        if msg.reply_to_message:
            return msg.reply_to_message.from_user

        if msg.entities:
            for e in msg.entities:
                if e.type == enums.MessageEntityType.TEXT_MENTION:
                    return e.user

        if msg.text:
            try:
                if m := re.search(r"@(\w{5,32})", msg.text):
                    return await app.get_users(m.group(0))
                if m := re.search(r"\b\d{6,15}\b", msg.text):
                    return await app.get_users(int(m.group(0)))
            except:
                pass

        return None


    async def play_log(
        self,
        m: types.Message,
        title: str,
        duration: str,
        bot_client = None
    ) -> None:
        client = bot_client or app
        logger_id = getattr(client, "logger", config.LOGGER_ID)
        if not logger_id or m.chat.id == logger_id:
            return
        try:
            _text = m.lang["play_log"].format(
                client.me.first_name,
                m.chat.id,
                m.chat.title,
                m.from_user.id,
                m.from_user.mention,
                m.link,
                title,
                duration,
            )
            await client.send_message(chat_id=logger_id, text=_text)
        except Exception as e:
            from NarzoxBots import logger
            logger.error(f"Error in play_log: {e}")

    async def send_log(self, m: types.Message, chat: bool = False) -> None:
        logger_id = getattr(app, "logger", config.LOGGER_ID)
        if not logger_id:
            return
        try:
            if chat:
                user = m.from_user
                return await app.send_message(
                    chat_id=logger_id,
                    text=m.lang["log_chat"].format(
                        m.chat.id,
                        m.chat.title,
                        user.id if user else 0,
                        user.mention if user else "NarzoxBotsmous",
                    ),
                )

            await app.send_message(
                chat_id=logger_id,
                text=m.lang["log_user"].format(
                    m.from_user.id,
                    f"@{m.from_user.username}",
                    m.from_user.mention,
                ),
            )
        except Exception as e:
            from NarzoxBots import logger
            logger.error(f"Error in send_log: {e}")
