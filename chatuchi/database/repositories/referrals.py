"""
Referrals repository.
"""

from typing import Optional

from database.db import Database


class ReferralsRepository:
    """Repository for referrals-related database operations."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def create_referral(
        self,
        inviter_id: int,
        referred_id: int,
    ) -> bool:
        """
        Create a referral relationship.
        
        Returns True if created, False if already exists.
        """
        try:
            await self.db.execute(
                """
                INSERT INTO referrals (inviter_id, referred_id, rewarded)
                VALUES (?, ?, 0)
                """,
                (inviter_id, referred_id),
            )
            return True
        except Exception:
            # Likely a unique constraint violation
            return False
    
    async def mark_rewarded(self, inviter_id: int, referred_id: int) -> bool:
        """Mark a referral as rewarded. Returns True if updated."""
        cursor = await self.db.execute(
            """
            UPDATE referrals 
            SET rewarded = 1 
            WHERE inviter_id = ? AND referred_id = ? AND rewarded = 0
            """,
            (inviter_id, referred_id),
        )
        return cursor.rowcount > 0
    
    async def is_rewarded(self, inviter_id: int, referred_id: int) -> bool:
        """Check if referral has been rewarded."""
        row = await self.db.execute(
            "SELECT rewarded FROM referrals WHERE inviter_id = ? AND referred_id = ?",
            (inviter_id, referred_id),
            fetch=True,
        )
        return row["rewarded"] if row else False
    
    async def get_referral(self, inviter_id: int, referred_id: int) -> Optional[dict]:
        """Get referral record."""
        row = await self.db.execute(
            "SELECT * FROM referrals WHERE inviter_id = ? AND referred_id = ?",
            (inviter_id, referred_id),
            fetch=True,
        )
        return dict(row) if row else None
    
    async def count_total_invitations(self, inviter_id: int) -> int:
        """Count total invitations sent by user."""
        row = await self.db.execute(
            "SELECT COUNT(*) as count FROM referrals WHERE inviter_id = ?",
            (inviter_id,),
            fetch=True,
        )
        return row["count"] if row else 0
    
    async def count_successful_referrals(self, inviter_id: int) -> int:
        """Count successful (rewarded) referrals."""
        row = await self.db.execute(
            "SELECT COUNT(*) as count FROM referrals WHERE inviter_id = ? AND rewarded = 1",
            (inviter_id,),
            fetch=True,
        )
        return row["count"] if row else 0
    
    async def count_rewards_earned(self, inviter_id: int) -> int:
        """Count total rewards earned from referrals."""
        row = await self.db.execute(
            "SELECT COUNT(*) as count FROM referrals WHERE inviter_id = ? AND rewarded = 1",
            (inviter_id,),
            fetch=True,
        )
        return row["count"] if row else 0
    
    async def get_referrer_id(self, referred_id: int) -> Optional[int]:
        """Get the inviter ID for a referred user."""
        row = await self.db.execute(
            "SELECT inviter_id FROM referrals WHERE referred_id = ?",
            (referred_id,),
            fetch=True,
        )
        return row["inviter_id"] if row else None
