"""
Blocks repository.
"""

from typing import Optional

from database.db import Database


class BlocksRepository:
    """Repository for blocks-related database operations."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def add_block(self, blocker_id: int, blocked_id: int) -> bool:
        """
        Add a block relationship.
        
        Returns True if block was added, False if already exists.
        """
        try:
            await self.db.execute(
                """
                INSERT INTO blocks (blocker_id, blocked_id)
                VALUES (?, ?)
                """,
                (blocker_id, blocked_id),
            )
            return True
        except Exception:
            # Likely a unique constraint violation
            return False
    
    async def remove_block(self, blocker_id: int, blocked_id: int) -> bool:
        """Remove a block. Returns True if block existed."""
        cursor = await self.db.execute(
            "DELETE FROM blocks WHERE blocker_id = ? AND blocked_id = ?",
            (blocker_id, blocked_id),
        )
        return cursor.rowcount > 0
    
    async def is_blocked(self, user_id_1: int, user_id_2: int) -> bool:
        """
        Check if either user has blocked the other.
        
        This is bidirectional - returns True if either has blocked the other.
        """
        row = await self.db.execute(
            """
            SELECT 1 FROM blocks 
            WHERE (blocker_id = ? AND blocked_id = ?)
               OR (blocker_id = ? AND blocked_id = ?)
            LIMIT 1
            """,
            (user_id_1, user_id_2, user_id_2, user_id_1),
            fetch=True,
        )
        return row is not None
    
    async def is_blocked_by(self, blocker_id: int, blocked_id: int) -> bool:
        """Check if specific user has blocked another."""
        row = await self.db.execute(
            "SELECT 1 FROM blocks WHERE blocker_id = ? AND blocked_id = ? LIMIT 1",
            (blocker_id, blocked_id),
            fetch=True,
        )
        return row is not None
    
    async def get_blocked_by_user(self, user_id: int) -> set[int]:
        """Get all users that this user has blocked."""
        rows = await self.db.execute(
            "SELECT blocked_id FROM blocks WHERE blocker_id = ?",
            (user_id,),
            fetch_all=True,
        )
        return {row["blocked_id"] for row in rows}
    
    async def get_users_who_blocked(self, user_id: int) -> set[int]:
        """Get all users who have blocked this user."""
        rows = await self.db.execute(
            "SELECT blocker_id FROM blocks WHERE blocked_id = ?",
            (user_id,),
            fetch_all=True,
        )
        return {row["blocker_id"] for row in rows}
