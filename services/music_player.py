"""Music player service with queue management."""
import logging
from typing import List, Optional
from database.manager import DatabaseManager
from database.models import Song, Queue
from services.youtube import YouTubeService

logger = logging.getLogger(__name__)


class MusicPlayer:
    """Advanced music player with queue management."""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize music player.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.youtube = YouTubeService()
        self.queues = {}  # In-memory queue cache

    async def search(self, query: str) -> List[Song]:
        """Search for songs.
        
        Args:
            query: Search query
            
        Returns:
            List of found songs
        """
        try:
            logger.info(f"Searching for: {query}")
            songs = await self.youtube.search(query)
            return songs
        except Exception as e:
            logger.error(f"Search error: {str(e)}", exc_info=True)
            return []

    async def add_to_queue(self, chat_id: int, song: Song, user_id: int) -> bool:
        """Add song to queue.
        
        Args:
            chat_id: Chat ID
            song: Song to add
            user_id: User ID
            
        Returns:
            Success status
        """
        try:
            song.added_by = user_id
            
            # Get or create queue
            queue_data = await self.db_manager.find_one(
                "queues",
                {"chat_id": chat_id}
            )
            
            if queue_data:
                await self.db_manager.update_one(
                    "queues",
                    {"chat_id": chat_id},
                    {"songs": queue_data.get("songs", []) + [song.dict()]}
                )
            else:
                await self.db_manager.insert_one(
                    "queues",
                    Queue(chat_id=chat_id, songs=[song]).dict()
                )
            
            logger.info(f"Added {song.title} to queue for chat {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding to queue: {str(e)}", exc_info=True)
            return False

    async def get_queue(self, chat_id: int) -> Optional[Queue]:
        """Get queue for chat.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            Queue object or None
        """
        try:
            queue_data = await self.db_manager.find_one(
                "queues",
                {"chat_id": chat_id}
            )
            
            if queue_data:
                return Queue(**queue_data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting queue: {str(e)}", exc_info=True)
            return None

    async def pause(self, chat_id: int) -> bool:
        """Pause playback.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            Success status
        """
        try:
            await self.db_manager.update_one(
                "queues",
                {"chat_id": chat_id},
                {"is_playing": False}
            )
            return True
        except Exception as e:
            logger.error(f"Pause error: {str(e)}", exc_info=True)
            return False

    async def resume(self, chat_id: int) -> bool:
        """Resume playback.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            Success status
        """
        try:
            await self.db_manager.update_one(
                "queues",
                {"chat_id": chat_id},
                {"is_playing": True}
            )
            return True
        except Exception as e:
            logger.error(f"Resume error: {str(e)}", exc_info=True)
            return False

    async def skip(self, chat_id: int) -> Optional[Song]:
        """Skip current song.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            Next song or None
        """
        try:
            queue = await self.get_queue(chat_id)
            if not queue or not queue.songs:
                return None
            
            if queue.current_position < len(queue.songs) - 1:
                queue.current_position += 1
                await self.db_manager.update_one(
                    "queues",
                    {"chat_id": chat_id},
                    {"current_position": queue.current_position}
                )
                return queue.songs[queue.current_position]
            
            return None
            
        except Exception as e:
            logger.error(f"Skip error: {str(e)}", exc_info=True)
            return None

    async def stop(self, chat_id: int) -> bool:
        """Stop playback and clear queue.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            Success status
        """
        try:
            await self.db_manager.delete_one(
                "queues",
                {"chat_id": chat_id}
            )
            return True
        except Exception as e:
            logger.error(f"Stop error: {str(e)}", exc_info=True)
            return False
