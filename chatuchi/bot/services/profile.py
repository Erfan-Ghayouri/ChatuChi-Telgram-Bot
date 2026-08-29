"""
Profile service for managing user profiles.
"""

from typing import Optional

from config import INITIAL_COINS
from database.db import Database
from database.repositories.users import UserRepository
from bot.utils.ids import generate_public_id


class ProfileService:
    """Service for profile-related operations."""
    
    def __init__(self, db: Database):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def create_profile(
        self,
        telegram_user_id: int,
        name: str,
        age: int,
        sex: str,
        city: Optional[str] = None,
        bio: str = "",
        referrer_public_id: Optional[str] = None,
    ) -> dict:
        """Create a new user profile."""
        # Get existing IDs to avoid collision
        existing_ids = await self.user_repo.get_all_public_ids()
        
        # Generate unique public ID
        public_id = generate_public_id(existing_ids)
        
        # Get referrer ID if provided
        referrer_id = None
        if referrer_public_id:
            referrer = await self.user_repo.get_by_public_id(referrer_public_id)
            if referrer:
                referrer_id = referrer["id"]
        
        # Create user
        user_id = await self.user_repo.create(
            telegram_user_id=telegram_user_id,
            public_id=public_id,
            name=name,
            age=age,
            sex=sex,
            city=city,
            bio=bio,
            referrer_id=referrer_id,
        )
        
        # Set initial coins
        await self.user_repo.update_coins(telegram_user_id, INITIAL_COINS)
        
        # Record initial coin transaction
        from database.repositories.wallet import WalletRepository
        wallet_repo = WalletRepository(self.db)
        await wallet_repo.add_transaction(
            user_id=user_id,
            amount=INITIAL_COINS,
            transaction_type="initial",
            description="Initial balance",
        )
        
        # Get created user
        user = await self.user_repo.get_by_telegram_id(telegram_user_id)
        return user
    
    async def get_user(self, telegram_user_id: int) -> Optional[dict]:
        """Get user by Telegram ID."""
        return await self.user_repo.get_by_telegram_id(telegram_user_id)
    
    async def get_user_by_public_id(self, public_id: str) -> Optional[dict]:
        """Get user by public ID."""
        return await self.user_repo.get_by_public_id(public_id)
    
    async def update_profile(
        self,
        telegram_user_id: int,
        **kwargs,
    ) -> None:
        """Update user profile fields."""
        await self.user_repo.update_profile(telegram_user_id, **kwargs)
    
    async def is_registered(self, telegram_user_id: int) -> bool:
        """Check if user is registered."""
        user = await self.get_user(telegram_user_id)
        return user is not None
    
    async def is_verified(self, telegram_user_id: int) -> bool:
        """Check if user's age is verified (18+)."""
        user = await self.get_user(telegram_user_id)
        return user is not None and user.get("is_verified_age") and user.get("age", 0) >= 18
