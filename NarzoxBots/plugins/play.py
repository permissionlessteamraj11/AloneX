# Copyright (c) 2025 NarzoxBots
# Licensed under the MIT License.
# This file is part of NarzoxBotsMusic
#ALONE-CODER

from pathlib import Path

from pyrogram import Client, filters, types

from NarzoxBots import anon, app, config, db, lang, queue, tg, yt, logger
from NarzoxBots.helpers import buttons, utils
from NarzoxBots.helpers._play import checkUB


def playlist_to_queue(chat_id: int, tracks: list) -> str:
    text = "<blockquote expandable>"
    for track in tracks:
        pos = queue.add(chat_id, track)
        text += f"<b>{pos}.</b> {track.title}\n"
    text = text[:1948] + "</blockquote>"
    return text

@Client.on_message(
    filters.command(["play", "playforce", "vplay", "vplayforce"])
    & filters.group
    & ~app.bl_users
)
@lang.language()
@checkUB
async def play_hndlr(
    client: Client,
    m: types.Message,
    force: bool = False,
    m3u8: bool = False,
    video: bool = False,
    url: str = None,
) -> None:
    try:
        is_clone = client.me.id != app.id
        clone_id = None
        if is_clone:
            for cid, cdata in db.json_db.data["clones"].items():
                if cdata.get("bot_username") == client.me.username:
                    clone_id = cid
                    break

        if not await db.get_feature_flag("music_enabled", clone_id):
            return # Silently ignore or send maintenance message

        sent = await m.reply_text(m.lang["play_searching"])
        file = None
        mention = m.from_user.mention
        media = tg.get_media(m.reply_to_message) if m.reply_to_message else None
        tracks = []

        if url:
            if "playlist" in url:
                await sent.edit_text(m.lang["playlist_fetch"])
                try:
                    tracks = await yt.playlist(
                        config.PLAYLIST_LIMIT, mention, url, video
                    )
                except Exception as e:
                    logger.error(f"Playlist Error: {e}")
                    return await sent.edit_text(m.lang["playlist_error"])

                if not tracks:
                    return await sent.edit_text(m.lang["playlist_error"])

                file = tracks[0]
                tracks.remove(file)
                file.message_id = sent.id
            else:
                file = await yt.search(url, sent.id, video=video)

            if not file:
                return await sent.edit_text(
                    m.lang["play_not_found"].format(config.SUPPORT_CHAT)
                )

        elif len(m.command) >= 2:
            query = " ".join(m.command[1:])
            file = await yt.search(query, sent.id, video=video)
            if not file:
                # Fallback search if the first one fails
                logger.warning(f"Initial search failed for: {query}. Trying fallback...")
                file = await yt.search(f"{query} official audio", sent.id, video=video)

            if not file:
                return await sent.edit_text(
                    m.lang["play_not_found"].format(config.SUPPORT_CHAT)
                )

        elif media:
            setattr(sent, "lang", m.lang)
            try:
                file = await tg.download(m.reply_to_message, sent)
            except Exception as e:
                logger.error(f"Telegram Download Error: {e}")
                return await sent.edit_text(m.lang["error_no_file"].format(config.SUPPORT_CHAT))

        if not file:
            return await sent.edit_text(m.lang["play_usage"])

        if file.duration_sec > config.DURATION_LIMIT:
            return await sent.edit_text(
                m.lang["play_duration_limit"].format(config.DURATION_LIMIT // 60)
            )

        if await db.is_logger():
            await utils.play_log(m, file.title, file.duration)

        file.user = mention
        if force:
            queue.force_add(m.chat.id, file)
        else:
            position = queue.add(m.chat.id, file)

            if position != 0 or await db.get_call(m.chat.id):
                await sent.edit_text(
                    m.lang["play_queued"].format(
                        position,
                        file.url,
                        file.title,
                        file.duration,
                        m.from_user.mention,
                    ),
                    reply_markup=buttons.play_queued(
                        m.chat.id, file.id, m.lang["play_now"]
                    ),
                )
                if tracks:
                    added = playlist_to_queue(m.chat.id, tracks)
                    await client.send_message(
                        chat_id=m.chat.id,
                        text=m.lang["playlist_queued"].format(len(tracks)) + added,
                    )
                return

        if not file.file_path:
            fname = f"downloads/{file.id}.{'mp4' if video else 'webm'}"
            if Path(fname).exists():
                file.file_path = fname
            else:
                await sent.edit_text(m.lang["play_downloading"])
                try:
                    file.file_path = await yt.download(file.id, video=video)
                except Exception as e:
                    logger.error(f"Download Error: {e}")
                    return await sent.edit_text(m.lang["play_not_found"].format(config.SUPPORT_CHAT))

        try:
            await anon.play_media(chat_id=m.chat.id, message=sent, media=file)
        except Exception as e:
            logger.error(f"Playback Error: {e}")
            return await sent.edit_text(f"An error occurred during playback: {e}")
        if not tracks:
            return
        added = playlist_to_queue(m.chat.id, tracks)
        await client.send_message(
            chat_id=m.chat.id,
            text=m.lang["playlist_queued"].format(len(tracks)) + added,
        )
    except Exception as e:
        logger.error(f"Error in play_hndlr: {e}")
        try:
            await m.reply_text("An unexpected error occurred while processing your request.")
        except:
            pass
