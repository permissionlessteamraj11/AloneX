"""Ultra-fast music handlers with instant responses."""
import logging
from kurigram import filters
from core.client import TelegramClient
from database.manager import DatabaseManager
from services.music_player import FastMusicPlayer
from services.cache import CacheManager
from utils.responses import error_message, success_message
import asyncio

logger = logging.getLogger(__name__)


class FastMusicHandler:
    """Ultra-fast handler for music commands."""

    def __init__(
        self,
        client: TelegramClient,
        db_manager: DatabaseManager,
        cache_manager: CacheManager
    ):
        """Initialize fast music handler.
        
        Args:
            client: Telegram client
            db_manager: Database manager
            cache_manager: Cache manager
        """
        self.client = client
        self.db_manager = db_manager
        self.cache_manager = cache_manager
        self.music_player = FastMusicPlayer(db_manager, cache_manager)

    async def handle_play(self, message) -> None:
        """Ultra-fast /play handler with instant feedback.
        
        Args:
            message: Message object
        """
        try:
            if not message.text or len(message.text.split(" ", 1)) < 2:
                await message.reply("❌ **Usage:** /play <song name or URL>")
                return
            
            query = message.text.split(" ", 1)[1]
            chat_id = message.chat.id
            user_id = message.from_user.id
            
            # Instant response
            status_msg = await message.reply(
                f"⚡ **Searching:** {query}...\n\n_Lightning fast search in progress_"
            )
            
            # Search in parallel
            songs = await self.music_player.search_fast(query, limit=3)
            
            if not songs:
                await status_msg.edit(
                    "❌ **No songs found.** Try a different search.\n\n"
                    "_Tip: Use song name or artist name_"
                )
                return
            
            song = songs[0]
            
            # Add to queue (non-blocking)
            success = await self.music_player.add_to_queue(chat_id, song, user_id)
            
            if success:
                await status_msg.edit(
                    f"✅ **Added to Queue**\n\n"
                    f"🎵 **{song.title}**\n"
                    f"🎤 *{song.artist}*\n"
                    f"⏱️ *Duration: {self._format_duration(song.duration)}*\n\n"
                    f"_Song added instantly to queue_",
                    parse_mode="markdown"
                )
                logger.info(f"⚡ Song added (instant): {song.title}")
            else:
                await status_msg.edit(error_message("Failed to add song"))
            
        except Exception as e:
            logger.error(f"Play handler error: {str(e)}", exc_info=True)
            await message.reply(error_message("Play command failed"))

    async def handle_pause(self, message) -> None:
        """Instant pause with no delay.
        
        Args:
            message: Message object
        """
        try:
            chat_id = message.chat.id
            await self.music_player.pause(chat_id)
            await message.reply("⏸️ **Music paused instantly**", parse_mode="markdown")
            logger.info(f"⚡ Paused (instant)")
            
        except Exception as e:
            logger.error(f"Pause error: {str(e)}", exc_info=True)
            await message.reply(error_message("Pause failed"))

    async def handle_resume(self, message) -> None:
        """Instant resume with no delay.
        
        Args:
            message: Message object
        """
        try:
            chat_id = message.chat.id
            await self.music_player.resume(chat_id)
            await message.reply("▶️ **Music resumed instantly**", parse_mode="markdown")
            logger.info(f"⚡ Resumed (instant)")
            
        except Exception as e:
            logger.error(f"Resume error: {str(e)}", exc_info=True)
            await message.reply(error_message("Resume failed"))

    async def handle_skip(self, message) -> None:
        """Instant skip to next song.
        
        Args:
            message: Message object
        """
        try:
            chat_id = message.chat.id
            next_song = await self.music_player.skip(chat_id)
            
            if next_song:
                await message.reply(
                    f"⏭️ **Skipped**\n\n"
                    f"🎵 **Now Playing:** {next_song.title}\n"
                    f"🎤 *{next_song.artist}*",
                    parse_mode="markdown"
                )
                logger.info(f"⚡ Skipped (instant): {next_song.title}")
            else:
                await message.reply(
                    "⏭️ **Queue ended** - No more songs\n\n"
                    "_Use /play to add more songs_",
                    parse_mode="markdown"
                )
                
        except Exception as e:
            logger.error(f"Skip error: {str(e)}", exc_info=True)
            await message.reply(error_message("Skip failed"))

    async def handle_queue(self, message) -> None:
        """Show queue with instant response.
        
        Args:
            message: Message object
        """
        try:
            chat_id = message.chat.id
            queue = await self.music_player.get_queue(chat_id)
            
            if not queue or not queue.songs:
                await message.reply(
                    "📋 **Queue is empty**\n\n"
                    "_Use /play to add songs to the queue_",
                    parse_mode="markdown"
                )
                return
            
            queue_text = "📋 **Current Queue**\n\n"
            queue_text += f"🎵 **Songs:** {len(queue.songs)}\n"
            queue_text += f"▶️ **Status:** {'Playing' if queue.is_playing else 'Paused'}\n\n"
            
            for i, song in enumerate(queue.songs[:10], 1):
                song_obj = song if not isinstance(song, dict) else song
                duration = self._format_duration(song_obj.get('duration', 0) if isinstance(song_obj, dict) else song_obj.duration)
                title = song_obj.get('title', 'Unknown') if isinstance(song_obj, dict) else song_obj.title
                artist = song_obj.get('artist', 'Unknown') if isinstance(song_obj, dict) else song_obj.artist
                queue_text += f"{i}. **{title}** - *{artist}* [{duration}]\n"
            
            if len(queue.songs) > 10:
                queue_text += f"\n... and {len(queue.songs) - 10} more songs"
            
            await message.reply(queue_text, parse_mode="markdown")
            logger.info(f"⚡ Queue shown (instant)")
            
        except Exception as e:
            logger.error(f"Queue error: {str(e)}", exc_info=True)
            await message.reply(error_message("Failed to show queue"))

    async def handle_stop(self, message) -> None:
        """Instant stop and clear queue.
        
        Args:
            message: Message object
        """
        try:
            chat_id = message.chat.id
            await self.music_player.stop(chat_id)
            await message.reply(
                "⏹️ **Music stopped**\n\n"
                "_Queue cleared - Use /play to start fresh_",
                parse_mode="markdown"
            )
            logger.info(f"⚡ Stopped (instant)")
            
        except Exception as e:
            logger.error(f"Stop error: {str(e)}", exc_info=True)
            await message.reply(error_message("Stop failed"))

    async def handle_now_playing(self, message) -> None:
        """Show currently playing song instantly.
        
        Args:
            message: Message object
        """
        try:
            chat_id = message.chat.id
            song = await self.music_player.get_current_playing(chat_id)
            
            if song:
                await message.reply(
                    f"🎵 **Now Playing**\n\n"
                    f"**{song.title}**\n"
                    f"🎤 *{song.artist}*\n"
                    f"⏱️ *{self._format_duration(song.duration)}*\n"
                    f"🔗 *[Watch on YouTube]({song.url})*",
                    parse_mode="markdown"
                )
            else:
                await message.reply(
                    "⏸️ **Nothing is playing**\n\n"
                    "_Use /play to start playing music_",
                    parse_mode="markdown"
                )
            
        except Exception as e:
            logger.error(f"Now playing error: {str(e)}", exc_info=True)
            await message.reply(error_message("Failed to get current song"))

    @staticmethod
    def _format_duration(seconds: int) -> str:
        """Format duration efficiently.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration
        """
        try:
            mins = int(seconds) // 60
            secs = int(seconds) % 60
            return f"{mins}:{secs:02d}"
        except:
            return "0:00"


async def setup(client: TelegramClient, db_manager: DatabaseManager, cache_manager: CacheManager):
    """Setup ultra-fast music handlers.
    
    Args:
        client: Telegram client
        db_manager: Database manager
        cache_manager: Cache manager
    """
    handler = FastMusicHandler(client, db_manager, cache_manager)
    
    # Register handlers
    async def wrapped_play(message):
        await handler.handle_play(message)
    
    async def wrapped_pause(message):
        await handler.handle_pause(message)
    
    async def wrapped_resume(message):
        await handler.handle_resume(message)
    
    async def wrapped_skip(message):
        await handler.handle_skip(message)
    
    async def wrapped_queue(message):
        await handler.handle_queue(message)
    
    async def wrapped_stop(message):
        await handler.handle_stop(message)
    
    async def wrapped_now_playing(message):
        await handler.handle_now_playing(message)
    
    client.add_handler(wrapped_play, filters=filters.command("play"))
    client.add_handler(wrapped_pause, filters=filters.command("pause"))
    client.add_handler(wrapped_resume, filters=filters.command("resume"))
    client.add_handler(wrapped_skip, filters=filters.command("skip"))
    client.add_handler(wrapped_queue, filters=filters.command("queue"))
    client.add_handler(wrapped_stop, filters=filters.command("stop"))
    client.add_handler(wrapped_now_playing, filters=filters.command("now"))
    
    logger.info("⚡ Ultra-fast music handlers registered")
