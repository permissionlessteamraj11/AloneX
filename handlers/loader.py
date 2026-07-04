"""Updated handler loader with cache support."""
import logging
import importlib
from pathlib import Path
from typing import Optional
from core.client import TelegramClient
from database.manager import DatabaseManager
from services.cache import CacheManager
from utils.decorators import log_execution

logger = logging.getLogger(__name__)


class HandlerLoader:
    """Load and register all handlers dynamically with cache support."""

    def __init__(
        self,
        client: TelegramClient,
        db_manager: DatabaseManager,
        cache_manager: CacheManager
    ):
        """Initialize handler loader.
        
        Args:
            client: Telegram client instance
            db_manager: Database manager instance
            cache_manager: Cache manager instance
        """
        self.client = client
        self.db_manager = db_manager
        self.cache_manager = cache_manager
        self.loaded_handlers = []

    @log_execution
    async def load_all_handlers(self) -> None:
        """Load all handlers from handlers directory."""
        try:
            handlers_dir = Path(__file__).parent
            handler_files = list(handlers_dir.glob("*.py"))
            handler_files = [f for f in handler_files if f.name != "__init__.py" and f.name != "loader.py"]
            
            logger.info(f"🔍 Found {len(handler_files)} handler modules")
            
            for handler_file in handler_files:
                await self._load_handler_module(handler_file)
            
            logger.info(f"⚡ Loaded {len(self.loaded_handlers)} handler modules")
            
        except Exception as e:
            logger.error(f"Error loading handlers: {str(e)}", exc_info=True)

    async def _load_handler_module(self, handler_file: Path) -> None:
        """Load a single handler module.
        
        Args:
            handler_file: Path to handler file
        """
        try:
            module_name = handler_file.stem
            spec = importlib.util.spec_from_file_location(f"handlers.{module_name}", handler_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Call setup function if exists
            if hasattr(module, "setup"):
                # Check if setup function expects cache_manager
                import inspect
                sig = inspect.signature(module.setup)
                
                if len(sig.parameters) >= 3:  # Has cache_manager parameter
                    await module.setup(self.client, self.db_manager, self.cache_manager)
                else:
                    await module.setup(self.client, self.db_manager)
                
                self.loaded_handlers.append(module_name)
                logger.info(f"✅ Loaded handler: {module_name}")
            
        except Exception as e:
            logger.error(f"Failed to load handler {handler_file.name}: {str(e)}", exc_info=True)
