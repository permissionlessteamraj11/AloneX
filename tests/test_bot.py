"""Unit tests for bot module."""
import pytest
import asyncio
from config import Config
from core.bot import AloneXBot


class TestAloneXBot:
    """Test suite for AloneXBot class."""

    @pytest.fixture
    def config(self):
        """Create test config."""
        return Config()

    @pytest.fixture
    def bot(self, config):
        """Create test bot instance."""
        return AloneXBot(config)

    def test_bot_initialization(self, bot):
        """Test bot initialization."""
        assert bot.config is not None
        assert bot.client is None
        assert bot.db_manager is None
        assert not bot.is_running

    @pytest.mark.asyncio
    async def test_bot_lifecycle(self, bot):
        """Test bot start and stop lifecycle."""
        # Note: This would need proper mocking in real tests
        assert not bot.is_running
