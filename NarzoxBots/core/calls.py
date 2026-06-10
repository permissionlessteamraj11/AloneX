# Copyright (c) 2025 NarzoxBots
# ALONE-CODER

from ntgcalls import (ConnectionNotFound, TelegramServerError,
                      RTMPStreamingUnsupported)
from pyrogram import Client
from pyrogram.errors import MessageIdInvalid, PeerIdInvalid
from pyrogram.types import InputMediaPhoto, Message
from pytgcalls import PyTgCalls, exceptions, types
from pytgcalls.pytgcalls_session import PyTgCallsSession

from NarzoxBots import app, config, db, lang, logger, queue, userbot, yt
from NarzoxBots.helpers import Media, Track, buttons, thumb


class TgCall:
    def __init__(self):
        self.clients = []
        self._assistant_map = {} # assistant_id: PyTgCalls
        self._bot_to_assistant = {} # bot_id: assistant_id

    def get_call_client(self, assistant_id: int):
        return self._assistant_map.get(assistant_id) or (
            self.clients[0] if self.clients else None
        )

    async def register_assistant(self, bot_id: int, assistant: Client):
        if assistant.me.id in self._assistant_map:
            self._bot_to_assistant[bot_id] = assistant.me.id
            return

        client = PyTgCalls(assistant, cache_duration=100)
        await client.start()
        self.clients.append(client)
        self._assistant_map[assistant.me.id] = client
        self._bot_to_assistant[bot_id] = assistant.me.id
        await self.decorators(client)
        logger.info(f"Registered custom assistant {assistant.me.id} for bot {bot_id}")

    async def unregister_assistant(self, bot_id: int):
        self._bot_to_assistant.pop(bot_id, None)

    async def pause(self, chat_id: int, bot_id: int = None) -> bool:
        assistant = await db.get_assistant(chat_id, bot_id=bot_id)
        client = self.get_call_client(assistant.me.id)
        if not client: return False
        await db.playing(chat_id, paused=True)
        return await client.pause(chat_id)

    async def resume(self, chat_id: int, bot_id: int = None) -> bool:
        assistant = await db.get_assistant(chat_id, bot_id=bot_id)
        client = self.get_call_client(assistant.me.id)
        if not client: return False
        await db.playing(chat_id, paused=False)
        return await client.resume(chat_id)

    async def stop(self, chat_id: int, bot_id: int = None) -> None:
        assistant = await db.get_assistant(chat_id, bot_id=bot_id)
        client = self.get_call_client(assistant.me.id)
        try:
            queue.clear(chat_id)
            await db.remove_call(chat_id)
        except: pass

        if client:
            try: await client.leave_call(chat_id)
            except: pass

    async def play_media(
        self,
        chat_id: int,
        message: Message,
        media: Media | Track,
        seek_time: int = 0,
        bot_id: int = None,
        retries: int = 0,
        dsp: dict = None
    ) -> None:
        assistant = await db.get_assistant(chat_id, bot_id=bot_id)
        client = self.get_call_client(assistant.me.id)
        if not client: return

        _lang = await lang.get_lang(chat_id)
        _thumb = (
            await thumb.generate(media)
            if isinstance(media, Track)
            else config.DEFAULT_THUMB
        )

        if not media.file_path:
            if retries < 2:
                media.file_path = await yt.download(media.id, video=media.video)
                return await self.play_media(chat_id, message, media, seek_time, bot_id, retries + 1, dsp)
            await message.edit_text(_lang["error_no_file"].format(config.SUPPORT_CHAT))
            return await self.play_next(chat_id)

        # DSP (Bass boost, speed)
        ffmpeg_args = []
        if dsp:
            if dsp.get("bass"):
                ffmpeg_args.append(f"bass=g={dsp['bass']}")
            if dsp.get("speed"):
                ffmpeg_args.append(f"atempo={dsp['speed']}")

        filter_str = f"-af \"{','.join(ffmpeg_args)}\"" if ffmpeg_args else ""

        stream = types.MediaStream(
            media_path=media.file_path,
            audio_parameters=types.AudioQuality.HIGH,
            video_parameters=types.VideoQuality.HD_720p,
            ffmpeg_parameters=(f"-ss {seek_time} " if seek_time > 1 else "") + f"{filter_str} -tune zerolatency -analyzeduration 0 -probesize 32",
        )
        try:
            try: await assistant.get_chat(chat_id)
            except: pass

            await client.play(chat_id=chat_id, stream=stream)
            if not seek_time:
                media.time = 1
                await db.add_call(chat_id)
                text = _lang["play_media"].format(media.url, media.title, media.duration, media.user)
                keyboard = buttons.controls(chat_id)
                try:
                    await message.edit_media(
                        media=InputMediaPhoto(media=_thumb, caption=text),
                        reply_markup=keyboard,
                    )
                except:
                    media.message_id = (await app.send_photo(
                        chat_id=chat_id, photo=_thumb, caption=text, reply_markup=keyboard
                    )).id
        except PeerIdInvalid:
            logger.error(f"PeerIdInvalid for chat {chat_id}. Attempting rejoin.")
            try: await assistant.join_chat(chat_id)
            except: pass
            if retries < 2: return await self.play_media(chat_id, message, media, seek_time, bot_id, retries + 1, dsp)
        except exceptions.NoActiveGroupCall:
            await self.stop(chat_id)
            await message.edit_text(_lang["error_no_call"])
        except Exception as e:
            logger.error(f"Playback Error: {e}")
            if retries < 2:
                media.file_path = await yt.download(media.id, video=media.video)
                return await self.play_media(chat_id, message, media, seek_time, bot_id, retries + 1, dsp)
            await self.stop(chat_id)
            await message.edit_text(f"Playback failed: {type(e).__name__}")

    async def play_next(self, chat_id: int, bot_id: int = None) -> None:
        media = queue.get_next(chat_id)
        serving_bot = await db.get_client(chat_id, bot_id=bot_id)

        if not media:
            return await self.stop(chat_id, bot_id=bot_id)

        _lang = await lang.get_lang(chat_id)
        msg = await serving_bot.send_message(chat_id=chat_id, text=_lang["play_next"])
        media.message_id = msg.id
        await self.play_media(chat_id, msg, media, bot_id=bot_id)

    async def decorators(self, client: PyTgCalls) -> None:
        @client.on_update()
        async def update_handler(_, update: types.Update) -> None:
            if isinstance(update, types.StreamEnded):
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
            self._assistant_map[ub.me.id] = client
            await self.decorators(client)
        logger.info("PyTgCalls client(s) started.")

    async def exit(self) -> None:
        for client in self.clients:
            try: await client.stop()
            except: pass
        logger.info("PyTgCalls client(s) stopped.")

anon = TgCall()
