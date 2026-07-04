"""High-speed YouTube search service with intelligent caching."""
import logging
from typing import List, Optional
from py_yt_search import search
from database.models import Song
from services.cache import CacheManager
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Thread pool for blocking operations
executor = ThreadPoolExecutor(max_workers=5)


class YouTubeService:
    """High-speed YouTube service with intelligent caching."""

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """Initialize YouTube service.
        
        Args:
            cache_manager: Cache manager instance
        """
        self.cache = cache_manager
        self._search_cache = {}

    async def search(self, query: str, limit: int = 5) -> List[Song]:
        """Search YouTube with intelligent caching.
        
        Args:
            query: Search query
            limit: Number of results
            
        Returns:
            List of Song objects
        """
        # Try cache first
        cache_key = f"yt_search:{query}:{limit}"
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached:
                logger.debug(f"🔥 Cache hit for: {query}")
                return [Song(**s) for s in cached]
        
        try:
            logger.info(f"🔍 Searching YouTube: {query}")
            
            # Run blocking search in thread pool for non-blocking behavior
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                executor,
                lambda: search(query, limit=limit)
            )
            
            songs = []
            for result in results[:limit]:
                try:
                    song = Song(
                        song_id=result.get("id", ""),
                        title=result.get("title", "Unknown"),
                        artist=result.get("channel", "Unknown"),
                        duration=result.get("duration", 0) or 180,
                        url=f"https://youtube.com/watch?v={result.get('id', '')}",
                        thumbnail=result.get("thumbnails", [{}])[0].get("url"),
                        source="youtube"
                    )
                    songs.append(song)
                except Exception as e:
                    logger.warning(f"Error parsing result: {str(e)}")
                    continue
            
            # Cache results (30 minutes)
            if self.cache and songs:
                await self.cache.set(
                    cache_key,
                    [s.dict() for s in songs],
                    ttl=1800
                )
            
            logger.info(f"✅ Found {len(songs)} songs for: {query}")
            return songs
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}", exc_info=True)
            return []

    async def get_video_info(self, video_id: str) -> Optional[dict]:
        """Get detailed video information with caching.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Video information dictionary
        """
        cache_key = f"yt_info:{video_id}"
        
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached:
                return cached
        
        try:
            # Placeholder for detailed fetch
            info = {"id": video_id, "cached": False}
            
            if self.cache:
                await self.cache.set(cache_key, info, ttl=3600)
            
            return info
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            return None

    async def clear_search_cache(self) -> None:
        """Clear YouTube search cache."""
        if self.cache:
            cleared = await self.cache.clear_pattern("yt_search:*")
            logger.info(f"Cleared {cleared} cached searches")
