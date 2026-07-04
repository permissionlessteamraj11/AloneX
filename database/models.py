"""Database models and schemas."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class User(BaseModel):
    """User model."""
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    is_premium: bool = False
    premium_expiry: Optional[datetime] = None
    total_plays: int = 0
    favorite_songs: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True


class Chat(BaseModel):
    """Chat/Group model."""
    chat_id: int
    chat_type: str  # group, supergroup, channel
    title: Optional[str] = None
    is_music_enabled: bool = True
    prefix: str = "/"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Song(BaseModel):
    """Song/Track model."""
    song_id: str
    title: str
    artist: str
    duration: int
    url: str
    thumbnail: Optional[str] = None
    source: str = "youtube"  # youtube, spotify, etc
    added_by: int
    added_at: datetime = Field(default_factory=datetime.utcnow)


class Queue(BaseModel):
    """Queue model for chat."""
    chat_id: int
    songs: List[Song] = []
    current_song: Optional[Song] = None
    current_position: int = 0
    is_playing: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Playlist(BaseModel):
    """Playlist model for users."""
    playlist_id: str
    user_id: int
    name: str
    description: Optional[str] = None
    songs: List[str] = []  # Song IDs
    is_public: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
