# Copyright (c) 2025 NarzoxBots
# Licensed under the MIT License.
# This file is part of NarzoxBotsMusic
#ALONE-CODER

import asyncio

from pyrogram import Client, enums, errors, types

from NarzoxBots import app, config, db, logger, queue, yt
from NarzoxBots.helpers import utils


def checkUB(play):
    async def wrapper(bot_client: Client, m: types.Message):
        if not m.from_user:
            return await m.reply_text(m.lang["play_user_invalid"])

        chat_id = m.chat.id
        if m.chat.type != enums.ChatType.SUPERGROUP:
            await m.reply_text(m.lang["play_chat_invalid"])
            return await bot_client.leave_chat(chat_id)

        if not m.reply_to_message and (
            len(m.command) < 2 or (len(m.command) == 2 and m.command[1] == "-f")
        ):
            return await m.reply_text(m.lang["play_usage"])

        if len(queue.get_queue(chat_id)) >= config.QUEUE_LIMIT:
            return await m.reply_text(m.lang["play_queue_full"].format(config.QUEUE_LIMIT))

        force = m.command[0].endswith("force") or (
            len(m.command) > 1 and "-f" in m.command[1]
        )
        video = m.command[0][0] == "v" and config.VIDEO_PLAY
        url = utils.get_url(m)
        m3u8 = url and not yt.valid(url)

        from NarzoxBots.helpers._permissions import permission

        # Check if the feature is globally disabled or specifically for this chat
        # (Feature flag check will be added in later steps)

        play_mode = await db.get_play_mode(chat_id)
        if play_mode or force:
            if not await permission.check_permission(chat_id, m.from_user.id, level="auth"):
                return await m.reply_text(m.lang["play_admin"])

        if chat_id not in db.active_calls:
            client = await db.get_assistant(chat_id, bot_id=bot_client.me.id)
            try:
                # Resolve peer to avoid PeerIdInvalid
                try:
                    await bot_client.get_users(client.me.username or client.me.id)
                except:
                    pass
                # Optimized: Try to get member status without full peer resolution if possible
                member = await bot_client.get_chat_member(chat_id, client.me.id)
                if member.status in [
                    enums.ChatMemberStatus.BANNED,
                    enums.ChatMemberStatus.RESTRICTED,
                ]:
                    try:
                        await bot_client.unban_chat_member(
                            chat_id=chat_id, user_id=client.me.id
                        )
                    except:
                        return await m.reply_text(
                            m.lang["play_banned"].format(
                                bot_client.me.first_name,
                                client.me.id,
                                client.me.mention,
                                f"@{client.me.username}" if client.me.username else None,
                            )
                        )
            except (errors.UserNotParticipant, errors.exceptions.bad_request_400.UserNotParticipant):
                if m.chat.username:
                    invite_link = m.chat.username
                    try:
                        pass
                    except:
                        pass
                else:
                    try:
                        chat_info = await bot_client.get_chat(chat_id)
                        invite_link = chat_info.invite_link
                        if not invite_link:
                            # Check if bot has permission to invite users
                            me_member = await bot_client.get_chat_member(chat_id, "me")
                            if me_member.privileges and me_member.privileges.can_invite_users:
                                invite_link = await bot_client.export_chat_invite_link(chat_id)
                            else:
                                return await m.reply_text(m.lang["admin_required"])
                    except errors.ChatAdminRequired:
                        return await m.reply_text(m.lang["admin_required"])
                    except Exception as ex:
                        return await m.reply_text(
                            m.lang["play_invite_error"].format(type(ex).__name__)
                        )

                umm = await m.reply_text(m.lang["play_invite"].format(bot_client.me.first_name))
                await asyncio.sleep(2)
                try:
                    await asyncio.wait_for(client.join_chat(invite_link), timeout=20)
                except asyncio.TimeoutError:
                    return await umm.edit_text("Assistant took too long to join. Please try again.")
                except errors.UserAlreadyParticipant:
                    pass
                except errors.InviteRequestSent:
                    await asyncio.sleep(2)
                    try:
                        await client.approve_chat_join_request(chat_id, client.me.id)
                    except errors.HideRequesterMissing:
                        pass
                    except Exception as ex:
                        return await umm.edit_text(
                            m.lang["play_invite_error"].format(type(ex).__name__)
                        )
                except Exception as ex:
                    logger.error(f"Error joining chat - {chat_id}: {ex}")
                    return await umm.edit_text(
                        m.lang["play_invite_error"].format(type(ex).__name__)
                    )

                await umm.delete()
                pass

        try:
            await m.delete()
        except:
            pass

        return await play(bot_client, m, force, m3u8, video, url)

    return wrapper
