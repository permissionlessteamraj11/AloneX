"""Telegram client wrapper with advanced features."""
import logging
from typing import Optional, Callable
from kurigram import Client, filters
from config import Config
from utils.decorators import log_execution

logger = logging.getLogger(__name__)


class TelegramClient:
    """Advanced wrapper around Kurigram Client."""

    def __init__(self, config: Config):
        """Initialize Telegram client.
        
        Args:
            config: Configuration instance
        """
        self.config = config
        self.client = Client(
            "AloneX",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN
        )
        self._is_connected = False
        self._handlers = []

    @log_execution
    async def initialize(self) -> None:
        """Initialize client connection."""
        try:
            logger.info("Initializing Telegram client...")
            # Client initialization if needed
            self._is_connected = True
            logger.info("✅ Telegram client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize client: {str(e)}", exc_info=True)
            raise

    @log_execution
    async def start(self) -> None:
        """Start receiving updates."""
        try:
            logger.info("Starting Telegram client...")
            await self.client.start()
            logger.info("✅ Telegram client started")
            await self.client.idle()
        except Exception as e:
            logger.error(f"Client start error: {str(e)}", exc_info=True)
            raise

    @log_execution
    async def stop(self) -> None:
        """Stop the client."""
        try:
            logger.info("Stopping Telegram client...")
            await self.client.stop()
            self._is_connected = False
            logger.info("✅ Telegram client stopped")
        except Exception as e:
            logger.error(f"Error stopping client: {str(e)}", exc_info=True)

    def add_handler(self, handler: Callable, filters_obj=None) -> None:
        """Register a message handler.
        
        Args:
            handler: Handler function
            filters_obj: Filter conditions
        """
        self.client.on_message(filters=filters_obj)(handler)
        self._handlers.append(handler)
        logger.debug(f"Handler registered: {handler.__name__}")

    def add_callback_handler(self, handler: Callable) -> None:
        """Register a callback query handler.
        
        Args:
            handler: Handler function
        """
        self.client.on_callback_query()(handler)
        self._handlers.append(handler)
        logger.debug(f"Callback handler registered: {handler.__name__}")

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._is_connected

    @property
    def handlers_count(self) -> int:
        """Get number of registered handlers."""
        return len(self._handlers)
