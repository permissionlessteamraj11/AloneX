"""Start command handler."""
import logging
from kurigram import filters
from core.client import TelegramClient
from database.manager import DatabaseManager
from utils.responses import start_message

logger = logging.getLogger(__name__)


async def handle_start(client: TelegramClient, message, db_manager: DatabaseManager):
    """Handle /start command.
    
    Args:
        client: Telegram client
        message: Message object
        db_manager: Database manager
    """
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "User"
        
        # Log user action
        logger.info(f"User {user_id} ({username}) triggered /start")
        
        # Send welcome message
        await message.reply(
            start_message(username),
            parse_mode="markdown"
        )
        
    except Exception as e:
        logger.error(f"Error in start handler: {str(e)}", exc_info=True)
        await message.reply("❌ An error occurred. Please try again.")


async def setup(client: TelegramClient, db_manager: DatabaseManager):
    """Setup start command handler.
    
    Args:
        client: Telegram client
        db_manager: Database manager
    """
    async def wrapped_start(message):
        await handle_start(client, message, db_manager)
    
    client.add_handler(wrapped_start, filters=filters.command("start"))
    logger.info("Start handler registered")
