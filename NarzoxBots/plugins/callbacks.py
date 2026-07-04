# Copyright (c) 2025 NarzoxBots
# Licensed under the MIT License.
# This file is part of NarzoxBotsMusic

import re
import asyncio
from pyrogram import Client, filters, types
from NarzoxBots import anon, app, db, lang, queue, tg, yt, logger
from NarzoxBots.helpers import admin_check, buttons, can_manage_vc


@Client.on_callback_query(filters.regex("cancel_dl") & ~app.bl_users)
@lang.language()
async def cancel_dl(client: Client, query: types.CallbackQuery):
    try:
        await query.answer()
        await tg.cancel(query)
    except Exception as e:
        print(f"Error in cancel_dl: {e}")


@Client.on_callback_query(filters.regex("controls") & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _controls(client: Client, query: types.CallbackQuery):
    try:
        args = query.data.split()
        action, chat_id = args[1], int(args[2])
        qaction = len(args) == 4
        user = query.from_user.mention

        if not await db.get_call(chat_id):
            return await query.answer(query.lang["not_playing"], show_alert=True)

        if action == "status":
            return await query.answer()
        await query.answer(query.lang["processing"], show_alert=True)

        reply = ""
        status = None

        if action == "pause":
            if not await db.playing(chat_id):
                return await query.answer(
                    query.lang["play_already_paused"], show_alert=True
                )
            await anon.pause(chat_id, bot_id=client.me.id)
            if qaction:
                return await query.edit_message_reply_markup(
                    reply_markup=buttons.queue_markup(chat_id, query.lang["paused"], False)
                )
            status = query.lang["paused"]
            reply = query.lang["play_paused"].format(user)

        elif action == "resume":
            if await db.playing(chat_id):
                return await query.answer(query.lang["play_not_paused"], show_alert=True)
            await anon.resume(chat_id, bot_id=client.me.id)
            if qaction:
                return await query.edit_message_reply_markup(
                    reply_markup=buttons.queue_markup(chat_id, query.lang["playing"], True)
                )
            reply = query.lang["play_resumed"].format(user)

        elif action == "skip":
            await anon.play_next(chat_id, bot_id=client.me.id)
            status = query.lang["skipped"]
            reply = query.lang["play_skipped"].format(user)

        elif action == "force":
            pos, media = queue.check_item(chat_id, args[3])
            if not media or pos == -1:
                return await query.edit_message_text(query.lang["play_expired"])

            m_id = queue.get_current(chat_id).message_id
            queue.force_add(chat_id, media, remove=pos)
            try:
                await client.delete_messages(
                    chat_id=chat_id, message_ids=[m_id, media.message_id], revoke=True
                )
                media.message_id = None
            except:
                pass

            msg = await client.send_message(chat_id=chat_id, text=query.lang["play_next"])
            if not media.file_path:
                media.file_path = await yt.download(media.id, video=media.video)
            media.message_id = msg.id
            return await anon.play_media(chat_id, msg, media, bot_id=client.me.id)

        elif action == "replay":
            media = queue.get_current(chat_id)
            media.user = user
            await anon.replay(chat_id, bot_id=client.me.id)
            status = query.lang["replayed"]
            reply = query.lang["play_replayed"].format(user)

        elif action == "stop":
            await anon.stop(chat_id, bot_id=client.me.id)
            status = query.lang["stopped"]
            reply = query.lang["play_stopped"].format(user)

        if action in ["skip", "replay", "stop"]:
            await query.message.reply_text(reply)
            await query.message.delete()
        else:
            mtext = re.sub(
                r"\n\n<blockquote>.*?</blockquote>",
                "",
                query.message.caption.html or query.message.text.html,
                flags=re.DOTALL,
            )
            keyboard = buttons.controls(
                chat_id, status=status if action != "resume" else None, _lang=query.lang
            )
            await query.edit_message_text(
                f"{mtext}\n\n<blockquote>{reply}</blockquote>", reply_markup=keyboard
            )
    except Exception as e:
        print(f"Error in _controls: {e}")
        await query.answer("An error occurred while processing the request.", show_alert=True)


@Client.on_callback_query(filters.regex(r"^help(_| )") & ~app.bl_users)
@lang.language()
async def _help(client: Client, query: types.CallbackQuery):
    try:
        data = query.data.split()
        # Handle help_cat category
        if query.data.startswith("help_cat"):
            cat = data[1]
            return await query.edit_message_text(
                text=query.lang[f"help_{cat}"],
                reply_markup=buttons.help_markup(query.lang, cat),
            )

        # Handle help main or help close
        action = data[1] if len(data) > 1 else "main"

        if action == "main":
            return await query.edit_message_text(
                text=query.lang["help_menu"], reply_markup=buttons.help_markup(query.lang, "main")
            )
        elif action == "close":
            try:
                await query.message.delete()
            except:
                pass
            return
    except Exception as e:
        print(f"Error in _help: {e}")


@Client.on_callback_query(filters.regex("clone_info") & ~app.bl_users)
@lang.language()
async def _clone_info(client: Client, query: types.CallbackQuery):
    try:
        await query.answer()
        await query.edit_message_text(
            text=query.lang["help_clone"],
            reply_markup=buttons.help_markup(query.lang, "clone")
        )
    except Exception as e:
        print(f"Error in _clone_info: {e}")


@Client.on_callback_query(filters.regex("settings") & ~app.bl_users)
@lang.language()
@admin_check
async def _settings_cb(client: Client, query: types.CallbackQuery):
    try:
        cmd = query.data.split()
        if len(cmd) == 1:
            return await query.answer()
        await query.answer(query.lang["processing"], show_alert=True)

        chat_id = query.message.chat.id
        _admin = await db.get_play_mode(chat_id)
        _delete = await db.get_cmd_delete(chat_id)
        _language = await db.get_lang(chat_id)

        if cmd[1] == "delete":
            _delete = not _delete
            await db.set_cmd_delete(chat_id, _delete)
        elif cmd[1] == "play":
            _admin = not _admin
            await db.set_play_mode(chat_id, _admin)

        await query.edit_message_reply_markup(
            reply_markup=buttons.settings_markup(
                query.lang,
                _admin,
                _delete,
                _language,
                chat_id,
            )
        )
    except Exception as e:
        print(f"Error in _settings_cb: {e}")


@Client.on_callback_query(filters.regex(r"^edit_") & ~app.bl_users)
async def _config_callbacks(client: Client, query: types.CallbackQuery):
    try:
        data = query.data
        clone_id = None
        clones = await db.get_clones()
        for cid, cdata in clones.items():
            if cdata.get("bot_username") == client.me.username:
                clone_id = cid
                break

        if not clone_id:
            return await query.answer("Unauthorized.", show_alert=True)

        settings = await db.get_settings(clone_id)
        if not settings or query.from_user.id != clones[clone_id].get("owner_id"):
            return await query.answer("Only the bot owner can use this.", show_alert=True)

        if data == "edit_welcome_config":
            field = "welcome_text"
            prompt = "Send the new welcome text."
        elif data == "edit_support_config":
            field = "support_link"
            prompt = "Send the new support link."
        elif data == "edit_updates_config":
            field = "updates_link"
            prompt = "Send the new updates link."
        elif data == "edit_group_config":
            field = "group_link"
            prompt = "Send the new group link."
        elif data == "edit_assistant_config":
            field = "assistant_session"
            prompt = "Send the new assistant session string."
        elif data.startswith("toggle_flag"):
            flag = data.split()[1]
            current_val = getattr(settings, flag, True if flag != "maintenance_mode" else False)
            await db.update_settings(clone_id, **{flag: not current_val})
            await query.answer(f"Toggled {flag.replace('_', ' ')}!")
            # Update the config message
            from NarzoxBots.plugins.owner_settings import bot_config
            return await bot_config(client, query.message)
        else:
            return await query.answer("Unknown action.")

        await query.answer()
        msg = await query.message.reply_text(prompt)

        try:
            # Note: listen requires a compatible client implementation or pyromod
            response = await client.listen(chat_id=query.message.chat.id, user_id=query.from_user.id, timeout=60)
            if response and response.text:
                await db.update_settings(clone_id, **{field: response.text})
                await response.reply_text(f"Successfully updated {field.replace('_', ' ')}!")
                await msg.delete()
        except asyncio.TimeoutError:
            await msg.edit_text("Timeout. Please try again.")
    except Exception as e:
        logger.error(f"Error in _config_callbacks: {e}")
