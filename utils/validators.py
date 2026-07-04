"""Input validators."""
from typing import Union


def validate_user_id(user_id: Union[int, str]) -> bool:
    """Validate user ID.
    
    Args:
        user_id: User ID to validate
        
    Returns:
        Validation result
    """
    try:
        uid = int(user_id)
        return uid > 0
    except (ValueError, TypeError):
        return False


def validate_chat_id(chat_id: Union[int, str]) -> bool:
    """Validate chat ID.
    
    Args:
        chat_id: Chat ID to validate
        
    Returns:
        Validation result
    """
    try:
        cid = int(chat_id)
        return cid != 0
    except (ValueError, TypeError):
        return False


def validate_url(url: str) -> bool:
    """Validate URL.
    
    Args:
        url: URL to validate
        
    Returns:
        Validation result
    """
    return url.startswith(("http://", "https://"))
