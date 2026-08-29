"""
Queue repository for matchmaking operations.
"""

from datetime import datetime, timedelta
from typing import Optional

from database.db import Database


class QueueRepository:
    """Repository for queue-related database operations."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def add(
        self,
        user_id: int,
        mode: str,
        sex_filter: Optional[str] = None,
        city_filter: Optional[str] = None,
    ) -> None:
        """Add user to matchmaking queue."""
        await self.db.execute(
            """
            INSERT OR REPLACE INTO queue (user_id, mode, sex_filter, city_filter, joined_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (user_id, mode, sex_filter, city_filter),
        )
    
    async def remove(self, user_id: int) -> bool:
        """Remove user from queue. Returns True if was in queue."""
        cursor = await self.db.execute(
            "DELETE FROM queue WHERE user_id = ?",
            (user_id,),
        )
        return cursor.rowcount > 0
    
    async def get(self, user_id: int) -> Optional[dict]:
        """Get queue entry for user."""
        row = await self.db.execute(
            "SELECT * FROM queue WHERE user_id = ?",
            (user_id,),
            fetch=True,
        )
        return dict(row) if row else None
    
    async def is_in_queue(self, user_id: int) -> bool:
        """Check if user is in queue."""
        row = await self.db.execute(
            "SELECT 1 FROM queue WHERE user_id = ? LIMIT 1",
            (user_id,),
            fetch=True,
        )
        return row is not None
    
    async def count(self) -> int:
        """Get total queue count."""
        row = await self.db.execute(
            "SELECT COUNT(*) as count FROM queue",
            fetch=True,
        )
        return row["count"] if row else 0
    
    async def find_match_random(
        self, 
        exclude_ids: set[int],
    ) -> Optional[dict]:
        """
        Find a random match from queue.
        
        Looks for users in 'waiting_random' mode.
        """
        placeholders = ",".join("?" * len(exclude_ids)) if exclude_ids else ""
        exclude_clause = f" AND user_id NOT IN ({placeholders})" if exclude_ids else ""
        
        query = f"""
            SELECT q.*, u.sex, u.city 
            FROM queue q
            JOIN users u ON q.user_id = u.id
            WHERE q.mode = 'random' 
            {exclude_clause}
            ORDER BY q.joined_at ASC
            LIMIT 1
        """
        
        params = tuple(exclude_ids) if exclude_ids else ()
        row = await self.db.execute(query, params, fetch=True)
        return dict(row) if row else None
    
    async def find_match_filtered(
        self,
        user_sex: str,
        user_city: Optional[str],
        sex_filter: Optional[str],
        city_filter: Optional[str],
        exclude_ids: set[int],
    ) -> Optional[dict]:
        """
        Find a filtered match from queue.
        
        Matches based on sex and/or city filters.
        """
        conditions = ["q.mode = 'filtered'"]
        params = []
        
        # Build filter conditions
        if sex_filter and sex_filter != "any":
            # We want someone whose sex matches our filter
            conditions.append("u.sex = ?")
            params.append(sex_filter)
        
        if city_filter and city_filter != "any":
            conditions.append("u.city = ?")
            params.append(city_filter)
        
        # Exclude certain IDs
        if exclude_ids:
            placeholders = ",".join("?" * len(exclude_ids))
            conditions.append(f"q.user_id NOT IN ({placeholders})")
            params.extend(exclude_ids)
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
            SELECT q.*, u.sex, u.city 
            FROM queue q
            JOIN users u ON q.user_id = u.id
            WHERE {where_clause}
            ORDER BY q.joined_at ASC
            LIMIT 1
        """
        
        row = await self.db.execute(query, tuple(params), fetch=True)
        return dict(row) if row else None
    
    async def cleanup_stale(self, max_age_seconds: int = 3600) -> int:
        """Remove stale queue entries. Returns count of removed entries."""
        cutoff = datetime.now() - timedelta(seconds=max_age_seconds)
        cursor = await self.db.execute(
            "DELETE FROM queue WHERE joined_at < ?",
            (cutoff,),
        )
        return cursor.rowcount
    
    async def get_all_waiting(self) -> list[dict]:
        """Get all users waiting in queue."""
        rows = await self.db.execute(
            """
            SELECT q.*, u.telegram_user_id, u.sex, u.city
            FROM queue q
            JOIN users u ON q.user_id = u.id
            ORDER BY q.joined_at ASC
            """,
            fetch_all=True,
        )
        return [dict(row) for row in rows]
