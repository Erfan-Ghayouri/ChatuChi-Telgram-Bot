"""
Moderation service for reports, blocks, and safety features.
"""

from database.db import Database
from database.repositories.users import UserRepository
from database.repositories.reports import ReportsRepository
from database.repositories.blocks import BlocksRepository
from database.repositories.likes import LikesRepository


class ModerationService:
    """Service for moderation-related operations."""
    
    def __init__(self, db: Database):
        self.db = db
        self.user_repo = UserRepository(db)
        self.reports_repo = ReportsRepository(db)
        self.blocks_repo = BlocksRepository(db)
        self.likes_repo = LikesRepository(db)
    
    async def submit_report(
        self,
        reporter_telegram_id: int,
        reported_public_id: str,
        reason: str,
        details: str = "",
    ) -> bool:
        """Submit a report against a user."""
        # Get reporter
        reporter = await self.user_repo.get_by_telegram_id(reporter_telegram_id)
        if not reporter:
            return False
        
        # Get reported user
        reported = await self.user_repo.get_by_public_id(reported_public_id)
        if not reported:
            return False
        
        # Create report
        await self.reports_repo.create_report(
            reporter_id=reporter["id"],
            reported_id=reported["id"],
            reason=reason,
            details=details,
        )
        
        return True
    
    async def block_user(
        self,
        blocker_telegram_id: int,
        blocked_public_id: str,
    ) -> bool:
        """Block a user."""
        # Get blocker
        blocker = await self.user_repo.get_by_telegram_id(blocker_telegram_id)
        if not blocker:
            return False
        
        # Get blocked user
        blocked = await self.user_repo.get_by_public_id(blocked_public_id)
        if not blocked:
            return False
        
        # Add block
        await self.blocks_repo.add_block(blocker["id"], blocked["id"])
        
        return True
    
    async def is_blocked(self, user1_telegram_id: int, user2_telegram_id: int) -> bool:
        """Check if users are blocked (either direction)."""
        user1 = await self.user_repo.get_by_telegram_id(user1_telegram_id)
        user2 = await self.user_repo.get_by_telegram_id(user2_telegram_id)
        
        if not user1 or not user2:
            return False
        
        return await self.blocks_repo.is_blocked(user1["id"], user2["id"])
    
    async def send_like(
        self,
        from_telegram_id: int,
        to_telegram_id: int,
    ) -> bool:
        """Send a like from one user to another."""
        from_user = await self.user_repo.get_by_telegram_id(from_telegram_id)
        to_user = await self.user_repo.get_by_telegram_id(to_telegram_id)
        
        if not from_user or not to_user:
            return False
        
        # Check if already liked
        if await self.likes_repo.has_liked(from_user["id"], to_user["id"]):
            return False
        
        # Add like
        added = await self.likes_repo.add_like(from_user["id"], to_user["id"])
        if not added:
            return False
        
        # Update counters
        await self.user_repo.increment_likes_received(to_telegram_id)
        await self.user_repo.increment_likes_given(from_telegram_id)
        
        return True
    
    async def has_liked(self, from_telegram_id: int, to_telegram_id: int) -> bool:
        """Check if user has already liked another."""
        from_user = await self.user_repo.get_by_telegram_id(from_telegram_id)
        to_user = await self.user_repo.get_by_telegram_id(to_telegram_id)
        
        if not from_user or not to_user:
            return False
        
        return await self.likes_repo.has_liked(from_user["id"], to_user["id"])
    
    async def get_pending_reports_count(self) -> int:
        """Get count of pending reports."""
        return await self.reports_repo.get_pending_count()
    
    async def get_pending_reports(self, limit: int = 50) -> list[dict]:
        """Get pending reports."""
        return await self.reports_repo.get_pending_reports(limit)
    
    async def get_report_count_for_user(self, telegram_user_id: int) -> int:
        """Get total report count for a user."""
        user = await self.user_repo.get_by_telegram_id(telegram_user_id)
        if not user:
            return 0
        return await self.reports_repo.count_reports_for_user(user["id"])
    
    async def get_likes_info(self, telegram_user_id: int) -> dict:
        """Get likes information for user."""
        user = await self.user_repo.get_by_telegram_id(telegram_user_id)
        if not user:
            return {"received": 0, "given": 0}
        return await self.likes_repo.get_total_likes(user["id"])
