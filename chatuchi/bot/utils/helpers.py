"""
General helper functions.
"""

import asyncio
from datetime import datetime
from functools import wraps
from typing import Callable, Any

from pyrogram.types import Message


def rate_limit(max_calls: int = 5, period: float = 60.0):
    """
    Rate limiting decorator for handlers.
    
    Args:
        max_calls: Maximum number of calls allowed
        period: Time period in seconds
    """
    call_times: dict[int, list[float]] = {}
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user ID from message
            message: Message | None = None
            for arg in args:
                if isinstance(arg, Message):
                    message = arg
                    break
            
            if not message or not message.from_user:
                return await func(*args, **kwargs)
            
            user_id = message.from_user.id
            now = datetime.now().timestamp()
            
            # Clean old entries
            if user_id in call_times:
                call_times[user_id] = [
                    t for t in call_times[user_id] 
                    if now - t < period
                ]
            else:
                call_times[user_id] = []
            
            # Check rate limit
            if len(call_times[user_id]) >= max_calls:
                return None  # Silently ignore rate-limited calls
            
            # Record this call
            call_times[user_id].append(now)
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


async def safe_edit_message(
    client: Any,
    chat_id: int,
    message_id: int,
    text: str,
    **kwargs,
) -> bool:
    """
    Safely edit a message, handling errors gracefully.
    
    Returns True if successful, False otherwise.
    """
    try:
        await client.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            **kwargs,
        )
        return True
    except Exception:
        return False


async def safe_delete_message(
    client: Any,
    chat_id: int,
    message_id: int,
) -> bool:
    """
    Safely delete a message, handling errors gracefully.
    
    Returns True if successful, False otherwise.
    """
    try:
        await client.delete_messages(
            chat_id=chat_id,
            message_ids=message_id,
        )
        return True
    except Exception:
        return False


def format_datetime(dt: datetime | None) -> str:
    """Format datetime for display."""
    if not dt:
        return "Never"
    return dt.strftime("%Y-%m-%d %H:%M")


def format_relative_time(dt: datetime | None) -> str:
    """Format relative time (e.g., '5 minutes ago')."""
    if not dt:
        return "Never"
    
    now = datetime.now()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        return dt.strftime("%Y-%m-%d")


async def async_lock(lock: asyncio.Lock):
    """Context manager for asyncio.Lock."""
    await lock.acquire()
    try:
        yield
    finally:
        lock.release()


def load_cities_data() -> dict:
    """Load Iran cities data from JSON file."""
    import json
    from pathlib import Path
    
    cities_file = Path(__file__).parent.parent.parent / "data" / "iran_cities.json"
    
    if not cities_file.exists():
        # Return minimal fallback data
        return {
            "Tehran": ["Tehran"],
            "Isfahan": ["Isfahan"],
            "Fars": ["Shiraz"],
        }
    
    with open(cities_file, "r", encoding="utf-8") as f:
        return json.load(f)
