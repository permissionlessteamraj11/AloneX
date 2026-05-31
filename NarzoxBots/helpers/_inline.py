# Copyright (c) 2025 NarzoxBots
# Licensed under the MIT License.
# This file is part of NarzoxBotsMusic
# ALONE-CODER

from pyrogram import enums, types

from NarzoxBots import app, config, lang
from NarzoxBots.core.lang import lang_codes


class Inline:
    def __init__(self):
        self.ikm = types.InlineKeyboardMarkup
        self.ikb = types.InlineKeyboardButton

    def cancel_dl(self, text) -> types.InlineKeyboardMarkup:
        return self.ikm([[self.ikb(text=text, callback_data=f"cancel_dl")]])

    def controls(
        self,
        chat_id: int,
        status: str = None,
        timer: str = None,
        remove: bool = False,
        _lang: dict = None) -> types.InlineKeyboardMarkup:
        _lang = _lang or {}
        keyboard = []
        if status:
            keyboard.append(
                [self.ikb(text=status, callback_data=f"controls status {chat_id}")]
            )
        elif timer:
            keyboard.append(
                [self.ikb(text=timer, callback_data=f"controls status {chat_id}")]
            )

        if not remove:
            keyboard.append(
                [
                    self.ikb(text="▷", callback_data=f"controls resume {chat_id}"),
                    self.ikb(text="II", callback_data="settings"),
                    self.ikb(
                        text=_lang.get("close", "⌯ 𝐂ʟσsє ⌯"),
                        callback_data="help close"),
                ]
            )
        return self.ikm(keyboard)


    def help_markup(
        self, _lang: dict, cat: str = "main", back: bool = False
    ) -> types.InlineKeyboardMarkup:
        if back or cat != "main":
            rows = [
                [
                    self.ikb(text=_lang["back"], callback_data="help main"),
                    self.ikb(text=_lang["close"], callback_data="help close"),
                ]
            ]
        else:
            cbs = ["admins", "auth", "blist", "stats", "sudo", "play", "queue", "lang"]
            buttons = [
                self.ikb(text=_lang[f"help_{cb}"], callback_data=f"help_cat {cb}")
                for cb in cbs
            ]
            rows = [buttons[i : i + 3] for i in range(0, len(buttons), 3)]
            rows.append([self.ikb(text=_lang["close"], callback_data="help close")])

        return self.ikm(rows)

    def lang_markup(self, _lang: str) -> types.InlineKeyboardMarkup:
        langs = lang.get_languages()

        buttons = [
            self.ikb(
                text=f"{name} ({code}) {'✔️' if code == _lang else ''}",
                callback_data=f"lang_change {code}")
            for code, name in langs.items()
        ]
        rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
        return self.ikm(rows)

    def ping_markup(self, text: str) -> types.InlineKeyboardMarkup:
        return self.ikm([[self.ikb(text=text, url=config.SUPPORT_CHAT)]])

    def play_queued(
        self, chat_id: int, item_id: str, _text: str, playing: bool = True
    ) -> types.InlineKeyboardMarkup:
        _action = "pause" if playing else "resume"
        return self.ikm(
            [
                [
                    self.ikb(
                        text=_text,
                        callback_data=f"controls {_action} {chat_id} q")
                ]
            ]
        )

    def settings_markup(
        self, lang: dict, admin_only: bool, cmd_delete: bool, language: str, chat_id: int
    ) -> types.InlineKeyboardMarkup:
        return self.ikm(
            [
                [
                    self.ikb(
                        text=lang["cd_delete"].format("✅" if cmd_delete else "❌"),
                        callback_data=f"settings cmd_delete {chat_id}"),
                    self.ikb(
                        text=lang["admin_only"].format("✅" if admin_only else "❌"),
                        callback_data=f"settings admin_only {chat_id}"),
                ],
                [
                    self.ikb(
                        text=lang["language"].format(language),
                        callback_data=f"settings language {chat_id}")
                ],
                [
                    self.ikb(
                        text=lang["close"],
                        callback_data="help close")
                ],
            ]
        )

    def start_key(
        self,
        _lang: dict,
        private: bool,
        bot_username: str,
        support: str,
        updates: str,
        owner: str,
        clone: str = None
    ) -> types.InlineKeyboardMarkup:
        if not private:
            return self.ikm(
                [
                    [
                        self.ikb(text=_lang["add_me"], url=f"https://t.me/{bot_username}?startgroup=true"),
                    ],
                    [
                        self.ikb(text=_lang["support"], url=support),
                        self.ikb(text=_lang["channel"], url=updates),
                    ]
                ]
            )

        return self.ikm(
            [
                [
                    self.ikb(text=_lang["add_me"], url=f"https://t.me/{bot_username}?startgroup=true"),
                ],
                [
                    self.ikb(text=_lang["help"], callback_data="help main"),
                ],
                [
                    self.ikb(text=_lang["support"], url=support),
                    self.ikb(text=_lang["channel"], url=updates),
                ],
                [
                    self.ikb(text=_lang["clone_btn"], callback_data="clone_info"),
                    self.ikb(text=_lang["owner_btn"], url=owner),
                ]
            ]
        )

    def yt_key(self, url: str) -> types.InlineKeyboardMarkup:
        return self.ikm(
            [
                [
                    self.ikb(text="🎬 𝐘ᴏᴜ𝐓ᴜʙᴇ", url=url),
                ]
            ]
        )

    def queue_markup(self, chat_id: int, text: str, playing: bool) -> types.InlineKeyboardMarkup:
        _action = "pause" if playing else "resume"
        return self.ikm(
            [
                [
                    self.ikb(text=text, callback_data=f"controls {_action} {chat_id}"),
                    self.ikb(text="𝐒ᴋɪᴘ", callback_data=f"controls skip {chat_id}"),
                    self.ikb(text="𝐒ᴛᴏᴘ", callback_data=f"controls stop {chat_id}"),
                ],
                [
                    self.ikb(text="⌯ 𝐂ʟσsє ⌯", callback_data="help close")
                ]
            ]
        )
