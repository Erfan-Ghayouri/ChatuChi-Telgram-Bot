"""
Wallet service for coin and transaction management.
"""

from config import REFERRAL_REWARD, FILTER_MATCH_COST
from database.db import Database
from database.repositories.users import UserRepository
from database.repositories.wallet import WalletRepository


class WalletService:
    """Service for wallet-related operations."""
    
    def __init__(self, db: Database):
        self.db = db
        self.user_repo = UserRepository(db)
        self.wallet_repo = WalletRepository(db)
    
    async def get_balance(self, telegram_user_id: int) -> int:
        """Get user's coin balance."""
        user = await self.user_repo.get_by_telegram_id(telegram_user_id)
        if not user:
            return 0
        return user.get("coins", 0)
    
    async def get_transactions(self, telegram_user_id: int, limit: int = 10) -> list[dict]:
        """Get recent transactions for user."""
        user = await self.user_repo.get_by_telegram_id(telegram_user_id)
        if not user:
            return []
        
        return await self.wallet_repo.get_recent_transactions(user["id"], limit)
    
    async def add_coins(
        self,
        telegram_user_id: int,
        amount: int,
        transaction_type: str,
        description: str = "",
    ) -> int:
        """
        Add coins to user balance.
        
        Returns new balance.
        """
        user = await self.user_repo.get_by_telegram_id(telegram_user_id)
        if not user:
            raise ValueError("User not found")
        
        # Update balance atomically
        new_balance = await self.user_repo.add_coins(telegram_user_id, amount)
        
        # Record transaction
        await self.wallet_repo.add_transaction(
            user_id=user["id"],
            amount=amount,
            transaction_type=transaction_type,
            description=description,
        )
        
        return new_balance
    
    async def can_afford_filtered_match(self, telegram_user_id: int) -> bool:
        """Check if user has enough coins for filtered match."""
        balance = await self.get_balance(telegram_user_id)
        return balance >= FILTER_MATCH_COST
    
    async def format_wallet_view(self, telegram_user_id: int) -> str:
        """Format wallet information for display."""
        from bot.texts import WALLET_VIEW, NO_TRANSACTIONS, TRANSACTION_TYPES
        
        balance = await self.get_balance(telegram_user_id)
        transactions = await self.get_transactions(telegram_user_id, limit=5)
        
        if transactions:
            tx_lines = []
            for tx in transactions:
                tx_type = TRANSACTION_TYPES.get(tx["transaction_type"], tx["transaction_type"])
                sign = "+" if tx["amount"] > 0 else ""
                tx_lines.append(f"• {tx_type}: {sign}{tx['amount']} coins")
            tx_text = "\n".join(tx_lines)
        else:
            tx_text = NO_TRANSACTIONS
        
        return WALLET_VIEW.format(
            balance=balance,
            transactions=tx_text,
            referral_reward=REFERRAL_REWARD,
            filter_cost=FILTER_MATCH_COST,
        )
