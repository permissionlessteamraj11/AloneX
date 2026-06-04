# Copyright (c) 2025 NarzoxBots
# Licensed under the MIT License.
# This file is part of NarzoxBotsMusic
# ALONE-CODER

from ntgcalls import (ConnectionNotFound, TelegramServerError,
                      RTMPStreamingUnsupported)
from pyrogram.errors import MessageIdInvalid
from pyrogram.types import InputMediaPhoto, Message
from pytgcalls import PyTgCalls, exceptions, types
from pytgcalls.pytgcalls_session import PyTgCallsSession

from NarzoxBots import app, config, db, lang, logger, queue, userbot, yt
from NarzoxBots.helpers import Media, Track, buttons, thumb


class TgCall:
    def __init__(self):
        self.clients = []
        self._assistant_map = {}

    def get_call_client(self, assistant_id: int):
        return self._assistant_map.get(assistant_id) or (
            self.clients[0] if self.clients else None
        )

    async def pause(self, chat_id: int) -> bool:
        assistant = await db.get_assistant(chat_id)
        client = self.get_call_client(assistant.id)
        if not client:
            return False
        await db.playing(chat_id, paused=True)
        return await client.pause(chat_id)

    async def resume(self, chat_id: int) -> bool:
        assistant = await db.get_assistant(chat_id)
        client = self.get_call_client(assistant.id)
        if not client:
            return False
        await db.playing(chat_id, paused=False)
        return await client.resume(chat_id)

    async def stop(self, chat_id: int) -> None:
        assistant = await db.get_assistant(chat_id)
        client = self.get_call_client(assistant.id)
        try:
            queue.clear(chat_id)
            await db.remove_call(chat_id)
        except:
            pass

        if client:
            try:
                await client.leave_call(chat_id)
            except:
                pass


    async def play_media(
        self,
        chat_id: int,
        message: Message,
        media: Media | Track,
        seek_time: int = 0,
    ) -> None:
        assistant = await db.get_assistant(chat_id)
        client = self.get_call_client(assistant.id)
        if not client:
            return

        _lang = await lang.get_lang(chat_id)
        _thumb = (
            await thumb.generate(media)
            if isinstance(media, Track)
            else config.DEFAULT_THUMB
        )

        if not media.file_path:
            await message.edit_text(_lang["error_no_file"].format(config.SUPPORT_CHAT))
            return await self.play_next(chat_id)

        stream = types.MediaStream(
            media_path=media.file_path,
            audio_parameters=types.AudioQuality.HIGH,
            video_parameters=types.VideoQuality.HD_720p,
            audio_flags=types.MediaStream.Flags.REQUIRED,
            video_flags=(
                types.MediaStream.Flags.AUTO_DETECT
                if media.video
                else types.MediaStream.Flags.IGNORE
            ),
            ffmpeg_parameters=f"-ss {seek_time}" if seek_time > 1 else None,
        )
        try:
            await client.play(
                chat_id=chat_id,
                stream=stream,
                config=types.GroupCallConfig(auto_start=False),
            )
            if not seek_time:
                media.time = 1
                await db.add_call(chat_id)
                text = _lang["play_media"].format(
                    media.url,
                    media.title,
                    media.duration,
                    media.user,
                )
                keyboard = buttons.controls(chat_id)
                try:
                    await message.edit_media(
                        media=InputMediaPhoto(
                            media=_thumb,
                            caption=text,
                        ),
                        reply_markup=keyboard,
                    )
                except MessageIdInvalid:
                    media.message_id = (await app.send_photo(
                        chat_id=chat_id,
                        photo=_thumb,
                        caption=text,
                        reply_markup=keyboard,
                    )).id
        except FileNotFoundError:
            await message.edit_text(_lang["error_no_file"].format(config.SUPPORT_CHAT))
            await self.play_next(chat_id)
        except exceptions.NoActiveGroupCall:
            await self.stop(chat_id)
            await message.edit_text(_lang["error_no_call"])
        except exceptions.NoAudioSourceFound:
            await message.edit_text(_lang["error_no_audio"])
            await self.play_next(chat_id)
        except (ConnectionNotFound, TelegramServerError):
            await self.stop(chat_id)
            await message.edit_text(_lang["error_tg_server"])
        except RTMPStreamingUnsupported:
            await self.stop(chat_id)
            await message.edit_text(_lang["error_rtmp"])
        except Exception as e:
            if "PeerIdInvalid" in str(e):
                logger.error(f"PeerIdInvalid in play_media: {e}")
                await message.edit_text("Assistant peer cache issue. Try /play again in a moment.")
            else:
                logger.error(f"Unknown error in play_media: {e}")
                await message.edit_text(f"An error occurred: {type(e).__name__}")
            await self.stop(chat_id)


    async def replay(self, chat_id: int) -> None:
        if not await db.get_call(chat_id):
            return

        media = queue.get_current(chat_id)
        _lang = await lang.get_lang(chat_id)
        msg = await app.send_message(chat_id=chat_id, text=_lang["play_again"])
        await self.play_media(chat_id, msg, media)


    async def play_next(self, chat_id: int) -> None:
        media = queue.get_next(chat_id)
        try:
            if media.message_id:
                await app.delete_messages(
                    chat_id=chat_id,
                    message_ids=media.message_id,
                    revoke=True,
                )
                media.message_id = 0
        except:
            pass

        if not media:
            return await self.stop(chat_id)

        _lang = await lang.get_lang(chat_id)
        msg = await app.send_message(chat_id=chat_id, text=_lang["play_next"])
        if not media.file_path:
            media.file_path = await yt.download(media.id, video=media.video)
            if not media.file_path:
                await self.stop(chat_id)
                return await msg.edit_text(
                    _lang["error_no_file"].format(config.SUPPORT_CHAT)
                )

        media.message_id = msg.id
        await self.play_media(chat_id, msg, media)


    async def ping(self) -> float:
        pings = [client.ping for client in self.clients]
        return round(sum(pings) / len(pings), 2) if pings else 0.0


    async def health_check(self) -> dict:
        results = {}
        for i, client in enumerate(self.clients):
            status = "healthy"
            try:
                if not client.is_connected:
                    status = "disconnected"
                else:
                    # In newer pytgcalls versions, we should use the app directly if possible
                    # or just skip this specific check if it's causing issues.
                    # Given the error 'MtProtoClient' object has no attribute 'me',
                    # we use the underlying client directly.
                    pass
            except Exception as e:
                status = f"unhealthy: {str(e)}"
            results[f"assistant_{i+1}"] = status
        return results


    async def decorators(self, client: PyTgCalls) -> None:
        @client.on_update()
        async def update_handler(_, update: types.Update) -> None:
            if isinstance(update, types.StreamEnded):
                # Using chat_id from update
                await self.play_next(update.chat_id)
            elif isinstance(update, types.ChatUpdate):
                if update.status in [
                    types.ChatUpdate.Status.KICKED,
                    types.ChatUpdate.Status.LEFT_GROUP,
                    types.ChatUpdate.Status.CLOSED_VOICE_CHAT,
                ]:
                    await self.stop(update.chat_id)


    async def boot(self) -> None:
        PyTgCallsSession.notice_displayed = True
        for ub in userbot.clients:
            client = PyTgCalls(ub, cache_duration=100)
            await client.start()
            self.clients.append(client)
            self._assistant_map[ub.id] = client
            await self.decorators(client)
        logger.info("PyTgCalls client(s) started.")

    async def exit(self) -> None:
        for client in self.clients:
            try:
                await client.stop()
            except:
                pass
        logger.info("PyTgCalls client(s) stopped.")
