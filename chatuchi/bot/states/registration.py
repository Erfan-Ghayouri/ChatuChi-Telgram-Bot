"""
Registration state machine for managing user registration flow.
"""

import aiosqlite
from typing import Optional, Dict, Any
from database.db import get_db


class RegistrationStates:
    """Manager for registration states stored in database."""
    
    @staticmethod
    async def set_state(telegram_id: int, state_data: Dict[str, Any]) -> None:
        """Set state for a user."""
        db = get_db()
        
        await db.execute("""
            INSERT OR REPLACE INTO registration_states (telegram_id, state_data, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (telegram_id, str(state_data)))
    
    @staticmethod
    async def get_state(telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get state for a user."""
        db = get_db()
        
        result = await db.execute(
            "SELECT state_data FROM registration_states WHERE telegram_id = ?",
            (telegram_id,),
            fetch=True
        )
        
        if result:
            # Parse the string representation of dict
            state_str = result["state_data"]
            # Simple parsing for our use case
            try:
                # Convert string representation to actual dict
                import ast
                return ast.literal_eval(state_str)
            except:
                return {}
        
        return None
    
    @staticmethod
    async def clear_state(telegram_id: int) -> None:
        """Clear state for a user."""
        db = get_db()
        await db.execute(
            "DELETE FROM registration_states WHERE telegram_id = ?",
            (telegram_id,)
        )
