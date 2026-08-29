"""
User repository for database operations.
"""

from datetime import datetime
from typing import Optional

from database.db import Database


class UserRepository:
    """Repository for user-related database operations."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def create(
        self,
        telegram_user_id: int,
        public_id: str,
        name: str,
        age: int,
        sex: str,
        city: Optional[str] = None,
        bio: str = "",
        referrer_id: Optional[int] = None,
    ) -> int:
        """Create a new user. Returns user ID."""
        cursor = await self.db.execute(
            """
            INSERT INTO users 
            (telegram_user_id, public_id, name, age, sex, city, bio, referrer_id, coins, is_verified_age)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 1)
            """,
            (telegram_user_id, public_id, name, age, sex, city, bio, referrer_id),
        )
        return cursor.lastrowid
    
    async def get_by_telegram_id(self, telegram_user_id: int) -> Optional[dict]:
        """Get user by Telegram ID."""
        row = await self.db.execute(
            "SELECT * FROM users WHERE telegram_user_id = ?",
            (telegram_user_id,),
            fetch=True,
        )
        return dict(row) if row else None
    
    async def get_by_public_id(self, public_id: str) -> Optional[dict]:
        """Get user by public ID."""
        row = await self.db.execute(
            "SELECT * FROM users WHERE public_id = ?",
            (public_id.upper(),),
            fetch=True,
        )
        return dict(row) if row else None
    
    async def get_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by internal ID."""
        row = await self.db.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
            fetch=True,
        )
        return dict(row) if row else None
    
    async def update_status(self, telegram_user_id: int, status: str) -> None:
        """Update user status."""
        await self.db.execute(
            """
            UPDATE users 
            SET status = ?, last_seen = CURRENT_TIMESTAMP 
            WHERE telegram_user_id = ?
            """,
            (status, telegram_user_id),
        )
    
    async def update_last_seen(self, telegram_user_id: int) -> None:
        """Update user's last seen timestamp."""
        await self.db.execute(
            "UPDATE users SET last_seen = CURRENT_TIMESTAMP WHERE telegram_user_id = ?",
            (telegram_user_id,),
        )
    
    async def update_coins(self, telegram_user_id: int, coins: int) -> None:
        """Update user's coin balance."""
        await self.db.execute(
            "UPDATE users SET coins = ? WHERE telegram_user_id = ?",
            (coins, telegram_user_id),
        )
    
    async def add_coins(self, telegram_user_id: int, amount: int) -> int:
        """Add coins to user balance atomically. Returns new balance."""
        # Use a transaction for atomicity
        async with self.db.connection:
            # Get current balance
            row = await self.db.execute(
                "SELECT coins FROM users WHERE telegram_user_id = ?",
                (telegram_user_id,),
                fetch=True,
            )
            if not row:
                raise ValueError("User not found")
            
            current = row["coins"]
            new_balance = max(0, current + amount)  # Prevent negative
            
            await self.db.execute(
                "UPDATE users SET coins = ? WHERE telegram_user_id = ?",
                (new_balance, telegram_user_id),
            )
            
            return new_balance
    
    async def update_profile(
        self,
        telegram_user_id: int,
        **kwargs,
    ) -> None:
        """Update user profile fields."""
        allowed_fields = {"name", "age", "sex", "city", "bio"}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return
        
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [telegram_user_id]
        
        await self.db.execute(
            f"UPDATE users SET {set_clause} WHERE telegram_user_id = ?",
            tuple(values),
        )
    
    async def ban_user(self, telegram_user_id: int) -> None:
        """Ban a user."""
        await self.db.execute(
            """
            UPDATE users 
            SET is_banned = 1, status = 'offline' 
            WHERE telegram_user_id = ?
            """,
            (telegram_user_id,),
        )
    
    async def unban_user(self, telegram_user_id: int) -> None:
        """Unban a user."""
        await self.db.execute(
            "UPDATE users SET is_banned = 0 WHERE telegram_user_id = ?",
            (telegram_user_id,),
        )
    
    async def increment_likes_received(self, telegram_user_id: int) -> int:
        """Increment likes received count. Returns new count."""
        async with self.db.connection:
            await self.db.execute(
                "UPDATE users SET likes_received = likes_received + 1 WHERE telegram_user_id = ?",
                (telegram_user_id,),
            )
            row = await self.db.execute(
                "SELECT likes_received FROM users WHERE telegram_user_id = ?",
                (telegram_user_id,),
                fetch=True,
            )
            return row["likes_received"] if row else 0
    
    async def increment_likes_given(self, telegram_user_id: int) -> int:
        """Increment likes given count. Returns new count."""
        async with self.db.connection:
            await self.db.execute(
                "UPDATE users SET likes_given = likes_given + 1 WHERE telegram_user_id = ?",
                (telegram_user_id,),
            )
            row = await self.db.execute(
                "SELECT likes_given FROM users WHERE telegram_user_id = ?",
                (telegram_user_id,),
                fetch=True,
            )
            return row["likes_given"] if row else 0
    
    async def get_all_public_ids(self) -> set[str]:
        """Get all existing public IDs."""
        rows = await self.db.execute(
            "SELECT public_id FROM users",
            fetch_all=True,
        )
        return {row["public_id"] for row in rows}
    
    async def count(self) -> int:
        """Get total user count."""
        row = await self.db.execute(
            "SELECT COUNT(*) as count FROM users",
            fetch=True,
        )
        return row["count"] if row else 0
    
    async def count_by_status(self, status: str) -> int:
        """Get count of users by status."""
        row = await self.db.execute(
            "SELECT COUNT(*) as count FROM users WHERE status = ?",
            (status,),
            fetch=True,
        )
        return row["count"] if row else 0
    
    async def count_banned(self) -> int:
        """Get count of banned users."""
        row = await self.db.execute(
            "SELECT COUNT(*) as count FROM users WHERE is_banned = 1",
            fetch=True,
        )
        return row["count"] if row else 0
    
    async def get_users_by_city(self, city: str, exclude_ids: set[int] = None) -> list[dict]:
        """Get users by city, optionally excluding certain IDs."""
        query = "SELECT * FROM users WHERE city = ? AND is_banned = 0 AND status != 'offline'"
        params = [city]
        
        if exclude_ids:
            placeholders = ",".join("?" * len(exclude_ids))
            query += f" AND id NOT IN ({placeholders})"
            params.extend(exclude_ids)
        
        rows = await self.db.execute(query, tuple(params), fetch_all=True)
        return [dict(row) for row in rows]
    
    async def get_users_by_sex(self, sex: str, exclude_ids: set[int] = None) -> list[dict]:
        """Get users by sex, optionally excluding certain IDs."""
        query = "SELECT * FROM users WHERE sex = ? AND is_banned = 0 AND status != 'offline'"
        params = [sex]
        
        if exclude_ids:
            placeholders = ",".join("?" * len(exclude_ids))
            query += f" AND id NOT IN ({placeholders})"
            params.extend(exclude_ids)
        
        rows = await self.db.execute(query, tuple(params), fetch_all=True)
        return [dict(row) for row in rows]
