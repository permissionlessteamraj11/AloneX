"""Main entry point for AloneX Bot."""
import asyncio
import logging
import signal
import sys
from config import Config
from core.bot import AloneXBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BotManager:
    """Manage bot lifecycle."""

    def __init__(self):
        """Initialize bot manager."""
        self.config = Config()
        self.bot = AloneXBot(self.config)
        self._loop = None

    async def run(self) -> None:
        """Run the bot."""
        try:
            logger.info("🚀 Starting AloneX Bot...")
            await self.bot.start()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Critical error: {str(e)}", exc_info=True)
        finally:
            await self.bot.stop()
            logger.info("✅ AloneX Bot stopped")

    def handle_signal(self, signum, frame):
        """Handle system signals.
        
        Args:
            signum: Signal number
            frame: Frame object
        """
        logger.info(f"Received signal {signum}")
        if self._loop:
            self._loop.stop()


async def main():
    """Main async entry point."""
    manager = BotManager()
    
    # Setup signal handlers
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, manager.handle_signal)
    
    await manager.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot terminated by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
