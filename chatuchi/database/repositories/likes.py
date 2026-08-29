"""
Likes repository.
"""

from typing import Optional

from database.db import Database


class LikesRepository:
    """Repository for likes-related database operations."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def add_like(self, from_user_id: int, to_user_id: int) -> bool:
        """
        Add a like from one user to another.
        
        Returns True if like was added, False if already exists.
        """
        try:
            await self.db.execute(
                """
                INSERT INTO likes (from_user, to_user)
                VALUES (?, ?)
                """,
                (from_user_id, to_user_id),
            )
            return True
        except Exception:
            # Likely a unique constraint violation (duplicate like)
            return False
    
    async def has_liked(self, from_user_id: int, to_user_id: int) -> bool:
        """Check if user has already liked another user."""
        row = await self.db.execute(
            "SELECT 1 FROM likes WHERE from_user = ? AND to_user = ? LIMIT 1",
            (from_user_id, to_user_id),
            fetch=True,
        )
        return row is not None
    
    async def get_likes_received(self, user_id: int) -> int:
        """Get count of likes received by user."""
        row = await self.db.execute(
            "SELECT COUNT(*) as count FROM likes WHERE to_user = ?",
            (user_id,),
            fetch=True,
        )
        return row["count"] if row else 0
    
    async def get_likes_given(self, user_id: int) -> int:
        """Get count of likes given by user."""
        row = await self.db.execute(
            "SELECT COUNT(*) as count FROM likes WHERE from_user = ?",
            (user_id,),
            fetch=True,
        )
        return row["count"] if row else 0
    
    async def get_total_likes(self, user_id: int) -> dict:
        """Get both likes received and given for a user."""
        row = await self.db.execute(
            """
            SELECT 
                (SELECT COUNT(*) FROM likes WHERE to_user = ?) as received,
                (SELECT COUNT(*) FROM likes WHERE from_user = ?) as given
            """,
            (user_id, user_id),
            fetch=True,
        )
        if row:
            return {"received": row["received"], "given": row["given"]}
        return {"received": 0, "given": 0}
