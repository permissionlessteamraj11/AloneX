"""Standardized response messages."""


def start_message(username: str) -> str:
    """Generate start message.
    
    Args:
        username: User's username
        
    Returns:
        Formatted start message
    """
    return f"""
🎵 **Welcome to AloneX Bot** 🎵

Hello {username}! 👋

I'm a super fast and powerful Telegram bot for streaming music in voice chats.

**Commands:**
/play <song> - Play a song
/pause - Pause music
/resume - Resume music
/skip - Skip current song
/queue - Show queue
/stop - Stop and clear queue
/help - Get help

**Features:**
✨ High-quality audio streaming
⚡ Super fast performance
🎵 YouTube music support
📋 Queue management
👥 Group support

Enjoy the music! 🎧
"""


def error_message(error: str) -> str:
    """Generate error message.
    
    Args:
        error: Error description
        
    Returns:
        Formatted error message
    """
    return f"❌ **Error:** {error}"


def success_message(message: str) -> str:
    """Generate success message.
    
    Args:
        message: Success message
        
    Returns:
        Formatted success message
    """
    return f"✅ {message}"


def help_message() -> str:
    """Generate help message.
    
    Returns:
        Formatted help message
    """
    return """
📚 **AloneX Bot Commands**

**Music Commands:**
/play <query> - Search and play a song
/pause - Pause current playback
/resume - Resume playback
/skip - Skip to next song
/queue - Display current queue
/stop - Stop playback and clear queue

**User Commands:**
/start - Show welcome message
/help - Show this help message
/profile - Show your profile

**Admin Commands:**
/settings - Bot settings
/stats - Show statistics

Need more help? Visit our support channel! 🚀
"""
