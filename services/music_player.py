"""Ultra-fast music player with optimized queue and caching."""
import logging
import asyncio
from typing import List, Optional
from database.manager import DatabaseManager
from database.models import Song, Queue
from services.youtube import YouTubeService
from services.cache import CacheManager
from datetime import datetime

logger = logging.getLogger(__name__)


class FastMusicPlayer:
    """Ultra-fast music player with optimized performance."""

    def __init__(self, db_manager: DatabaseManager, cache_manager: CacheManager):
        """Initialize music player.
        
        Args:
            db_manager: Database manager
            cache_manager: Cache manager
        """
        self.db = db_manager
        self.cache = cache_manager
        self.youtube = YouTubeService(cache_manager)
        self.queues = {}  # In-memory queue cache for ultra-fast access
        self.now_playing = {}  # Current song tracking

    async def search_fast(self, query: str, limit: int = 5) -> List[Song]:
        """Ultra-fast search with parallel caching.
        
        Args:
            query: Search query
            limit: Number of results
            
        Returns:
            List of Song objects
        """
        logger.info(f"⚡ Fast search: {query}")
        return await self.youtube.search(query, limit)

    async def add_to_queue(self, chat_id: int, song: Song, user_id: int) -> bool:
        """Add song to queue with ultra-fast response.
        
        Args:
            chat_id: Chat ID
            song: Song to add
            user_id: User ID
            
        Returns:
            Success status
        """
        try:
            song.added_by = user_id
            
            # Check in-memory cache first
            cache_key = f"queue:{chat_id}"
            queue_data = self.queues.get(cache_key)
            
            if not queue_data:
                # Fallback to database
                queue_data = await self.db.find_one("queues", {"chat_id": chat_id})
            
            if queue_data:
                # Add to existing queue
                songs = queue_data.get("songs", [])
                songs.append(song.dict())
                
                # Update both database and memory
                await asyncio.gather(
                    self.db.update_one(
                        "queues",
                        {"chat_id": chat_id},
                        {"songs": songs, "updated_at": datetime.utcnow()}
                    ),
                    self.cache.set(cache_key, queue_data, ttl=3600)
                )
            else:
                # Create new queue
                new_queue = Queue(
                    chat_id=chat_id,
                    songs=[song]
                ).dict()
                
                await asyncio.gather(
                    self.db.insert_one("queues", new_queue),
                    self.cache.set(cache_key, new_queue, ttl=3600)
                )
            
            # Update in-memory cache
            self.queues[cache_key] = queue_data
            
            logger.info(f"✅ Added to queue (⚡ instant): {song.title}")
            return True
            
        except Exception as e:
            logger.error(f"Queue add error: {str(e)}", exc_info=True)
            return False

    async def get_queue(self, chat_id: int) -> Optional[Queue]:
        """Get queue with ultra-fast response from memory cache.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            Queue object or None
        """
        try:
            cache_key = f"queue:{chat_id}"
            
            # Check in-memory first (nanoseconds)
            if cache_key in self.queues:
                logger.debug(f"🔥 Memory hit for queue")
                queue_data = self.queues[cache_key]
                return Queue(**queue_data) if queue_data else None
            
            # Check Redis (milliseconds)
            if self.cache:
                queue_data = await self.cache.get(cache_key)
                if queue_data:
                    logger.debug(f"⚡ Redis hit for queue")
                    self.queues[cache_key] = queue_data
                    return Queue(**queue_data)
            
            # Fallback to database
            queue_data = await self.db.find_one("queues", {"chat_id": chat_id})
            if queue_data:
                logger.debug(f"📊 DB hit for queue")
                self.queues[cache_key] = queue_data
                if self.cache:
                    await self.cache.set(cache_key, queue_data, ttl=3600)
                return Queue(**queue_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Queue get error: {str(e)}", exc_info=True)
            return None

    async def skip(self, chat_id: int) -> Optional[Song]:
        """Skip to next song with ultra-fast response.
        
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
                
                # Update in-memory cache first (instant)
                cache_key = f"queue:{chat_id}"
                self.queues[cache_key] = queue.dict()
                
                # Update other caches in background
                asyncio.create_task(
                    asyncio.gather(
                        self.db.update_one(
                            "queues",
                            {"chat_id": chat_id},
                            {"current_position": queue.current_position}
                        ),
                        self.cache.set(cache_key, queue.dict(), ttl=3600)
                    )
                )
                
                logger.info(f"⏭️ Skipped (⚡ instant)")
                return queue.songs[queue.current_position]
            
            return None
            
        except Exception as e:
            logger.error(f"Skip error: {str(e)}", exc_info=True)
            return None

    async def pause(self, chat_id: int) -> bool:
        """Pause music instantly.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            Success status
        """
        try:
            cache_key = f"queue:{chat_id}"
            
            # Update in-memory (instant)
            if cache_key in self.queues:
                self.queues[cache_key]["is_playing"] = False
            
            # Update other caches in background
            asyncio.create_task(
                asyncio.gather(
                    self.db.update_one(
                        "queues",
                        {"chat_id": chat_id},
                        {"is_playing": False}
                    ),
                    self.cache.set(
                        cache_key,
                        self.queues.get(cache_key),
                        ttl=3600
                    )
                )
            )
            
            logger.info(f"⏸️ Paused (⚡ instant)")
            return True
        except Exception as e:
            logger.error(f"Pause error: {str(e)}", exc_info=True)
            return False

    async def resume(self, chat_id: int) -> bool:
        """Resume music instantly.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            Success status
        """
        try:
            cache_key = f"queue:{chat_id}"
            
            # Update in-memory (instant)
            if cache_key in self.queues:
                self.queues[cache_key]["is_playing"] = True
            
            # Update other caches in background
            asyncio.create_task(
                asyncio.gather(
                    self.db.update_one(
                        "queues",
                        {"chat_id": chat_id},
                        {"is_playing": True}
                    ),
                    self.cache.set(
                        cache_key,
                        self.queues.get(cache_key),
                        ttl=3600
                    )
                )
            )
            
            logger.info(f"▶️ Resumed (⚡ instant)")
            return True
        except Exception as e:
            logger.error(f"Resume error: {str(e)}", exc_info=True)
            return False

    async def stop(self, chat_id: int) -> bool:
        """Stop playback instantly.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            Success status
        """
        try:
            cache_key = f"queue:{chat_id}"
            
            # Remove from in-memory (instant)
            if cache_key in self.queues:
                del self.queues[cache_key]
            
            # Remove from other caches in background
            asyncio.create_task(
                asyncio.gather(
                    self.db.delete_one("queues", {"chat_id": chat_id}),
                    self.cache.delete(cache_key)
                )
            )
            
            logger.info(f"⏹️ Stopped (⚡ instant)")
            return True
        except Exception as e:
            logger.error(f"Stop error: {str(e)}", exc_info=True)
            return False

    async def get_current_playing(self, chat_id: int) -> Optional[Song]:
        """Get currently playing song with instant response.
        
        Args:
            chat_id: Chat ID
            
        Returns:
            Currently playing song or None
        """
        try:
            # Check memory first
            if chat_id in self.now_playing:
                return self.now_playing[chat_id]
            
            queue = await self.get_queue(chat_id)
            if queue and queue.is_playing and queue.songs:
                song = queue.songs[queue.current_position]
                self.now_playing[chat_id] = Song(**song) if isinstance(song, dict) else song
                return self.now_playing[chat_id]
            
            return None
        except Exception as e:
            logger.error(f"Error getting current song: {str(e)}")
            return None

    def clear_memory_cache(self, chat_id: Optional[int] = None) -> None:
        """Clear in-memory cache for performance.
        
        Args:
            chat_id: Specific chat to clear, or None to clear all
        """
        if chat_id:
            self.queues.pop(f"queue:{chat_id}", None)
            self.now_playing.pop(chat_id, None)
        else:
            self.queues.clear()
            self.now_playing.clear()
        logger.debug(f"Memory cache cleared")
