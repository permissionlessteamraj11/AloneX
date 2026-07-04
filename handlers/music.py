"""Music playback handlers."""
import logging
from typing import Optional
from kurigram import filters
from core.client import TelegramClient
from database.manager import DatabaseManager
from services.music_player import MusicPlayer
from utils.responses import error_message, success_message

logger = logging.getLogger(__name__)


class MusicHandler:
    """Handler for music-related commands."""

    def __init__(self, client: TelegramClient, db_manager: DatabaseManager):
        """Initialize music handler.
        
        Args:
            client: Telegram client
            db_manager: Database manager
        """
        self.client = client
        self.db_manager = db_manager
        self.music_player = MusicPlayer(db_manager)

    async def handle_play(self, message) -> None:
        """Handle /play command.
        
        Args:
            message: Message object
        """
        try:
            if not message.text or len(message.text.split(" ", 1)) < 2:
                await message.reply("❌ Usage: /play <song name or URL>")
                return
            
            query = message.text.split(" ", 1)[1]
            chat_id = message.chat.id
            user_id = message.from_user.id
            
            status_msg = await message.reply("🔍 Searching for song...")
            
            # Search for song
            songs = await self.music_player.search(query)
            if not songs:
                await status_msg.edit("❌ No songs found. Try a different search.")
                return
            
            song = songs[0]
            await self.music_player.add_to_queue(chat_id, song, user_id)
            
            await status_msg.edit(
                f"✅ Added to queue: **{song.title}** by {song.artist}",
                parse_mode="markdown"
            )
            logger.info(f"Song added to queue: {song.title}")
            
        except Exception as e:
            logger.error(f"Error in play handler: {str(e)}", exc_info=True)
            await message.reply(error_message("Failed to play song"))

    async def handle_pause(self, message) -> None:
        """Handle /pause command.
        
        Args:
            message: Message object
        """
        try:
            chat_id = message.chat.id
            await self.music_player.pause(chat_id)
            await message.reply("⏸️ Music paused")
            
        except Exception as e:
            logger.error(f"Error in pause handler: {str(e)}", exc_info=True)
            await message.reply(error_message("Failed to pause music"))

    async def handle_resume(self, message) -> None:
        """Handle /resume command.
        
        Args:
            message: Message object
        """
        try:
            chat_id = message.chat.id
            await self.music_player.resume(chat_id)
            await message.reply("▶️ Music resumed")
            
        except Exception as e:
            logger.error(f"Error in resume handler: {str(e)}", exc_info=True)
            await message.reply(error_message("Failed to resume music"))

    async def handle_skip(self, message) -> None:
        """Handle /skip command.
        
        Args:
            message: Message object
        """
        try:
            chat_id = message.chat.id
            next_song = await self.music_player.skip(chat_id)
            
            if next_song:
                await message.reply(
                    f"⏭️ Skipped. Now playing: **{next_song.title}**",
                    parse_mode="markdown"
                )
            else:
                await message.reply("⏭️ Queue ended")
                
        except Exception as e:
            logger.error(f"Error in skip handler: {str(e)}", exc_info=True)
            await message.reply(error_message("Failed to skip song"))

    async def handle_queue(self, message) -> None:
        """Handle /queue command.
        
        Args:
            message: Message object
        """
        try:
            chat_id = message.chat.id
            queue = await self.music_player.get_queue(chat_id)
            
            if not queue or not queue.songs:
                await message.reply("📋 Queue is empty")
                return
            
            queue_text = "📋 **Current Queue:**\n\n"
            for i, song in enumerate(queue.songs, 1):
                duration = self._format_duration(song.duration)
                queue_text += f"{i}. {song.title} - {song.artist} [{duration}]\n"
            
            await message.reply(queue_text, parse_mode="markdown")
            
        except Exception as e:
            logger.error(f"Error in queue handler: {str(e)}", exc_info=True)
            await message.reply(error_message("Failed to get queue"))

    async def handle_stop(self, message) -> None:
        """Handle /stop command.
        
        Args:
            message: Message object
        """
        try:
            chat_id = message.chat.id
            await self.music_player.stop(chat_id)
            await message.reply("⏹️ Music stopped. Queue cleared.")
            
        except Exception as e:
            logger.error(f"Error in stop handler: {str(e)}", exc_info=True)
            await message.reply(error_message("Failed to stop music"))

    @staticmethod
    def _format_duration(seconds: int) -> str:
        """Format duration in seconds to MM:SS format.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}:{secs:02d}"


async def setup(client: TelegramClient, db_manager: DatabaseManager):
    """Setup music handlers.
    
    Args:
        client: Telegram client
        db_manager: Database manager
    """
    handler = MusicHandler(client, db_manager)
    
    # Register music command handlers
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
    
    client.add_handler(wrapped_play, filters=filters.command("play"))
    client.add_handler(wrapped_pause, filters=filters.command("pause"))
    client.add_handler(wrapped_resume, filters=filters.command("resume"))
    client.add_handler(wrapped_skip, filters=filters.command("skip"))
    client.add_handler(wrapped_queue, filters=filters.command("queue"))
    client.add_handler(wrapped_stop, filters=filters.command("stop"))
    
    logger.info("Music handlers registered")
