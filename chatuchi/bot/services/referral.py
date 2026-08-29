"""
Referral service for managing referrals and rewards.
"""

from config import REFERRAL_REWARD
from database.db import Database
from database.repositories.users import UserRepository
from database.repositories.referrals import ReferralsRepository
from database.repositories.wallet import WalletRepository


class ReferralService:
    """Service for referral-related operations."""
    
    def __init__(self, db: Database):
        self.db = db
        self.user_repo = UserRepository(db)
        self.referral_repo = ReferralsRepository(db)
        self.wallet_repo = WalletRepository(db)
    
    async def create_referral(self, inviter_id: int, referred_id: int) -> bool:
        """
        Create a referral relationship.
        
        Returns True if created successfully.
        """
        return await self.referral_repo.create_referral(inviter_id, referred_id)
    
    async def reward_referral(self, inviter_telegram_id: int, referred_id: int) -> bool:
        """
        Reward inviter for successful referral.
        
        Returns True if reward was given.
        """
        # Get inviter user
        inviter = await self.user_repo.get_by_telegram_id(inviter_telegram_id)
        if not inviter:
            return False
        
        # Check if already rewarded
        if await self.referral_repo.is_rewarded(inviter["id"], referred_id):
            return False
        
        # Mark as rewarded
        if not await self.referral_repo.mark_rewarded(inviter["id"], referred_id):
            return False
        
        # Add coins
        await self.user_repo.add_coins(inviter_telegram_id, REFERRAL_REWARD)
        
        # Record transaction
        await self.wallet_repo.add_transaction(
            user_id=inviter["id"],
            amount=REFERRAL_REWARD,
            transaction_type="referral",
            description=f"Referral reward for user #{referred_id}",
        )
        
        return True
    
    async def get_referral_stats(self, telegram_user_id: int) -> dict:
        """Get referral statistics for user."""
        user = await self.user_repo.get_by_telegram_id(telegram_user_id)
        if not user:
            return {
                "total": 0,
                "successful": 0,
                "earned": 0,
            }
        
        total = await self.referral_repo.count_total_invitations(user["id"])
        successful = await self.referral_repo.count_successful_referrals(user["id"])
        earned = await self.referral_repo.count_rewards_earned(user["id"])
        
        return {
            "total": total,
            "successful": successful,
            "earned": earned,
        }
    
    async def generate_referral_link(self, public_id: str, bot_username: str) -> str:
        """Generate referral link for user."""
        # Remove CC- prefix for cleaner link
        clean_id = public_id.replace("CC-", "")
        return f"https://t.me/{bot_username}?start=ref_{clean_id}"
    
    async def extract_referrer_from_start_param(self, start_param: str) -> str | None:
        """
        Extract referrer public ID from start parameter.
        
        Expected format: ref_CC7F42A9 or ref_7F42A9
        """
        if not start_param or not start_param.startswith("ref_"):
            return None
        
        ref_code = start_param[4:]  # Remove 'ref_' prefix
        
        # Reconstruct full public ID
        if not ref_code.startswith("CC-"):
            ref_code = f"CC-{ref_code}"
        
        # Validate format
        user = await self.user_repo.get_by_public_id(ref_code)
        if user:
            return ref_code
        
        return None
    
    async def format_referral_view(
        self, 
        telegram_user_id: int, 
        bot_username: str,
    ) -> str:
        """Format referral information for display."""
        from bot.texts import REFERRAL_INFO
        
        user = await self.user_repo.get_by_telegram_id(telegram_user_id)
        if not user:
            return ""
        
        stats = await self.get_referral_stats(telegram_user_id)
        link = await self.generate_referral_link(user["public_id"], bot_username)
        
        return REFERRAL_INFO.format(
            link=link,
            total=stats["total"],
            successful=stats["successful"],
            earned=stats["earned"],
            reward=REFERRAL_REWARD,
        )
