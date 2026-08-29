"""
Utility functions for generating unique IDs and other helpers.
"""

import secrets
import string
from typing import Optional

from config import PUBLIC_ID_PREFIX, PUBLIC_ID_LENGTH


def generate_public_id(existing_ids: set[str] | None = None) -> str:
    """
    Generate a unique public ID in format CC-XXXXXX
    
    Args:
        existing_ids: Set of existing IDs to avoid collisions
        
    Returns:
        Unique public ID string
    """
    if existing_ids is None:
        existing_ids = set()
    
    chars = string.ascii_uppercase + string.digits
    max_attempts = 100
    
    for _ in range(max_attempts):
        random_part = ''.join(secrets.choice(chars) for _ in range(PUBLIC_ID_LENGTH))
        public_id = f"{PUBLIC_ID_PREFIX}{random_part}"
        
        if public_id not in existing_ids:
            return public_id
    
    # Fallback with longer ID if collision after max attempts
    random_part = ''.join(secrets.choice(chars) for _ in range(PUBLIC_ID_LENGTH + 2))
    return f"{PUBLIC_ID_PREFIX}{random_part}"


def validate_public_id(public_id: str) -> bool:
    """
    Validate public ID format.
    
    Args:
        public_id: The public ID to validate
        
    Returns:
        True if valid format
    """
    if not public_id.startswith(PUBLIC_ID_PREFIX):
        return False
    
    suffix = public_id[len(PUBLIC_ID_PREFIX):]
    if len(suffix) < PUBLIC_ID_LENGTH - 2 or len(suffix) > PUBLIC_ID_LENGTH + 2:
        return False
    
    allowed_chars = set(string.ascii_uppercase + string.digits)
    return all(c in allowed_chars for c in suffix)


def extract_public_id(text: str) -> Optional[str]:
    """
    Extract public ID from text (e.g., from command arguments).
    
    Args:
        text: Text that may contain a public ID
        
    Returns:
        Public ID if found, None otherwise
    """
    parts = text.split()
    for part in parts:
        # Try to find pattern like CC-7F42A9
        if part.upper().startswith(PUBLIC_ID_PREFIX):
            candidate = part.upper()
            if validate_public_id(candidate):
                return candidate
    return None


def format_coin_amount(amount: int) -> str:
    """Format coin amount with proper sign."""
    if amount > 0:
        return f"+{amount}"
    elif amount < 0:
        return str(amount)
    return "0"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis if too long."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def sanitize_input(text: str, max_length: int = 500) -> str:
    """Sanitize user input by stripping and limiting length."""
    if not text:
        return ""
    return text.strip()[:max_length]
