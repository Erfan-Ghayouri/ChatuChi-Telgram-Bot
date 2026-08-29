"""
Connection repository for active chat connections.
"""

from datetime import datetime, timedelta
from typing import Optional

from database.db import Database


class ConnectionRepository:
    """Repository for connection-related database operations."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def create(self, user_a_id: int, user_b_id: int) -> int:
        """Create a new connection. Returns connection ID."""
        cursor = await self.db.execute(
            """
            INSERT INTO connections (user_a, user_b, started_at, active)
            VALUES (?, ?, CURRENT_TIMESTAMP, 1)
            """,
            (user_a_id, user_b_id),
        )
        return cursor.lastrowid
    
    async def end_connection(self, connection_id: int) -> None:
        """End a connection."""
        await self.db.execute(
            """
            UPDATE connections 
            SET active = 0, ended_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            """,
            (connection_id,),
        )
    
    async def end_by_user(self, user_id: int) -> bool:
        """End connection for a specific user. Returns True if connection was ended."""
        # Find active connection
        conn = await self.get_active_for_user(user_id)
        if not conn:
            return False
        
        await self.end_connection(conn["id"])
        return True
    
    async def get_active_for_user(self, user_id: int) -> Optional[dict]:
        """Get active connection for a user."""
        row = await self.db.execute(
            """
            SELECT * FROM connections 
            WHERE (user_a = ? OR user_b = ?) AND active = 1
            LIMIT 1
            """,
            (user_id, user_id),
            fetch=True,
        )
        return dict(row) if row else None
    
    async def get_partner_id(self, user_id: int, connection_id: int) -> Optional[int]:
        """Get partner's user ID for a connection."""
        row = await self.db.execute(
            """
            SELECT CASE 
                WHEN user_a = ? THEN user_b 
                ELSE user_a 
            END as partner_id
            FROM connections 
            WHERE id = ? AND (user_a = ? OR user_b = ?)
            """,
            (user_id, connection_id, user_id, user_id),
            fetch=True,
        )
        return row["partner_id"] if row else None
    
    async def is_connected(self, user_id: int) -> bool:
        """Check if user is in an active connection."""
        row = await self.db.execute(
            "SELECT 1 FROM connections WHERE (user_a = ? OR user_b = ?) AND active = 1 LIMIT 1",
            (user_id, user_id),
            fetch=True,
        )
        return row is not None
    
    async def count_active(self) -> int:
        """Get count of active connections."""
        row = await self.db.execute(
            "SELECT COUNT(*) as count FROM connections WHERE active = 1",
            fetch=True,
        )
        return row["count"] if row else 0
    
    async def cleanup_stale(self, max_age_seconds: int = 7200) -> int:
        """Remove stale connections. Returns count of cleaned up connections."""
        cutoff = datetime.now() - timedelta(seconds=max_age_seconds)
        cursor = await self.db.execute(
            """
            UPDATE connections 
            SET active = 0, ended_at = ? 
            WHERE active = 1 AND started_at < ?
            """,
            (datetime.now(), cutoff),
        )
        return cursor.rowcount
    
    async def get_all_active(self) -> list[dict]:
        """Get all active connections."""
        rows = await self.db.execute(
            "SELECT * FROM connections WHERE active = 1",
            fetch_all=True,
        )
        return [dict(row) for row in rows]
