"""Utility decorators."""
import asyncio
import functools
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


def log_execution(func: Callable) -> Callable:
    """Decorator to log function execution.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs) -> Any:
        func_name = func.__name__
        logger.debug(f"Executing: {func_name}")
        try:
            result = await func(*args, **kwargs)
            logger.debug(f"Completed: {func_name}")
            return result
        except Exception as e:
            logger.error(f"Error in {func_name}: {str(e)}", exc_info=True)
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs) -> Any:
        func_name = func.__name__
        logger.debug(f"Executing: {func_name}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Completed: {func_name}")
            return result
        except Exception as e:
            logger.error(f"Error in {func_name}: {str(e)}", exc_info=True)
            raise
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
