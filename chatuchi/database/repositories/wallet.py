"""
Wallet transactions repository.
"""

from datetime import datetime
from typing import Optional

from database.db import Database


class WalletRepository:
    """Repository for wallet transaction operations."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def add_transaction(
        self,
        user_id: int,
        amount: int,
        transaction_type: str,
        description: Optional[str] = None,
    ) -> int:
        """Add a wallet transaction. Returns transaction ID."""
        cursor = await self.db.execute(
            """
            INSERT INTO wallet_transactions (user_id, amount, transaction_type, description)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, amount, transaction_type, description),
        )
        return cursor.lastrowid
    
    async def get_recent_transactions(
        self, 
        user_id: int, 
        limit: int = 10,
    ) -> list[dict]:
        """Get recent transactions for a user."""
        rows = await self.db.execute(
            """
            SELECT * FROM wallet_transactions 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
            """,
            (user_id, limit),
            fetch_all=True,
        )
        return [dict(row) for row in rows]
    
    async def get_total_earned(self, user_id: int) -> int:
        """Get total coins earned by user."""
        row = await self.db.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM wallet_transactions WHERE user_id = ? AND amount > 0",
            (user_id,),
            fetch=True,
        )
        return row["total"] if row else 0
    
    async def get_total_spent(self, user_id: int) -> int:
        """Get total coins spent by user."""
        row = await self.db.execute(
            "SELECT COALESCE(SUM(ABS(amount)), 0) as total FROM wallet_transactions WHERE user_id = ? AND amount < 0",
            (user_id,),
            fetch=True,
        )
        return row["total"] if row else 0
    
    async def count_by_type(
        self, 
        user_id: int, 
        transaction_type: str,
    ) -> int:
        """Count transactions of a specific type."""
        row = await self.db.execute(
            "SELECT COUNT(*) as count FROM wallet_transactions WHERE user_id = ? AND transaction_type = ?",
            (user_id, transaction_type),
            fetch=True,
        )
        return row["count"] if row else 0
