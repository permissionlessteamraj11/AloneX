"""YouTube search and fetch service."""
import logging
from typing import List, Optional
from py_yt_search import search
from database.models import Song

logger = logging.getLogger(__name__)


class YouTubeService:
    """YouTube video search and information service."""

    async def search(self, query: str, limit: int = 5) -> List[Song]:
        """Search for videos on YouTube.
        
        Args:
            query: Search query
            limit: Number of results
            
        Returns:
            List of Song objects
        """
        try:
            logger.debug(f"Searching YouTube for: {query}")
            results = search(query)
            
            songs = []
            for result in results[:limit]:
                try:
                    song = Song(
                        song_id=result.get("id", ""),
                        title=result.get("title", "Unknown"),
                        artist=result.get("channel", "Unknown"),
                        duration=result.get("duration", 0),
                        url=f"https://youtube.com/watch?v={result.get('id', '')}",
                        thumbnail=result.get("thumbnails", [{}])[0].get("url"),
                        source="youtube"
                    )
                    songs.append(song)
                except Exception as e:
                    logger.warning(f"Error parsing result: {str(e)}")
                    continue
            
            logger.info(f"Found {len(songs)} songs for query: {query}")
            return songs
            
        except Exception as e:
            logger.error(f"YouTube search error: {str(e)}", exc_info=True)
            return []

    async def get_video_info(self, video_id: str) -> Optional[dict]:
        """Get detailed video information.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Video information dictionary
        """
        try:
            # TODO: Implement detailed video fetch
            return {}
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}", exc_info=True)
            return None
