"""Updated core bot with cache integration."""
import asyncio
import logging
from typing import Optional
from kurigram import Client
from config import Config
from core.client import TelegramClient
from database.manager import DatabaseManager
from services.logger import Logger
from services.cache import CacheManager
from handlers.loader import HandlerLoader
from utils.decorators import log_execution

logger = logging.getLogger(__name__)


class AloneXBot:
    """Advanced Telegram VC Music Bot with ultra-fast responses."""

    def __init__(self, config: Config):
        """Initialize bot with configuration.
        
        Args:
            config: Configuration instance
        """
        self.config = config
        self.client: Optional[TelegramClient] = None
        self.db_manager: Optional[DatabaseManager] = None
        self.cache_manager: Optional[CacheManager] = None
        self.logger = Logger(__name__)
        self.handler_loader: Optional[HandlerLoader] = None
        self._is_running = False

    @log_execution
    async def initialize(self) -> None:
        """Initialize all bot components."""
        try:
            self.logger.info("🚀 Initializing AloneX Bot...")
            
            # Validate configuration
            self.config.check()
            
            # Initialize Telegram client
            self.client = TelegramClient(self.config)
            await self.client.initialize()
            
            # Initialize cache first (for ultra-fast responses)
            self.cache_manager = CacheManager(self.config.REDIS_URL)
            await self.cache_manager.connect()
            
            # Initialize database
            self.db_manager = DatabaseManager(self.config)
            await self.db_manager.connect()
            
            # Load handlers with cache
            self.handler_loader = HandlerLoader(
                self.client,
                self.db_manager,
                self.cache_manager
            )
            await self.handler_loader.load_all_handlers()
            
            self.logger.info("✅ AloneX Bot initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Initialization failed: {str(e)}", exc_info=True)
            raise

    @log_execution
    async def start(self) -> None:
        """Start the bot."""
        if self._is_running:
            self.logger.warning("Bot is already running")
            return
        
        try:
            await self.initialize()
            self._is_running = True
            self.logger.info("⚡ AloneX Bot started - Ultra-fast mode active")
            await self.client.start()
        except Exception as e:
            self.logger.error(f"Failed to start bot: {str(e)}", exc_info=True)
            raise

    @log_execution
    async def stop(self) -> None:
        """Stop the bot gracefully."""
        try:
            self.logger.info("🛑 Stopping AloneX Bot...")
            self._is_running = False
            
            if self.client:
                await self.client.stop()
            
            if self.cache_manager:
                await self.cache_manager.disconnect()
            
            if self.db_manager:
                await self.db_manager.disconnect()
            
            self.logger.info("✅ AloneX Bot stopped")
        except Exception as e:
            self.logger.error(f"Error stopping bot: {str(e)}", exc_info=True)

    @property
    def is_running(self) -> bool:
        """Check if bot is running."""
        return self._is_running
