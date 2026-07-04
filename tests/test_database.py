"""Unit tests for database module."""
import pytest
from database.models import User, Song, Playlist
from datetime import datetime


class TestDatabaseModels:
    """Test suite for database models."""

    def test_user_model(self):
        """Test User model creation."""
        user = User(
            user_id=123456,
            username="testuser",
            first_name="Test"
        )
        assert user.user_id == 123456
        assert user.username == "testuser"
        assert not user.is_premium

    def test_song_model(self):
        """Test Song model creation."""
        song = Song(
            song_id="dQw4w9WgXcQ",
            title="Test Song",
            artist="Test Artist",
            duration=180,
            url="https://youtube.com/watch?v=dQw4w9WgXcQ"
        )
        assert song.title == "Test Song"
        assert song.duration == 180
        assert song.source == "youtube"

    def test_playlist_model(self):
        """Test Playlist model creation."""
        playlist = Playlist(
            playlist_id="pl123",
            user_id=123456,
            name="My Playlist"
        )
        assert playlist.name == "My Playlist"
        assert len(playlist.songs) == 0
