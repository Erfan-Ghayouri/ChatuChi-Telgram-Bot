"""
Wallet command handlers.
"""

from pyrogram import Client, filters
from pyrogram.types import Message
from bot.texts import WALLET_VIEW, NO_TRANSACTIONS, TRANSACTION_TYPES
from config import REFERRAL_REWARD, FILTER_MATCH_COST


def register_wallet_handlers(app: Client, wallet_service):
    """Register wallet handlers."""
    
    @app.on_message(filters.command("wallet") & filters.private)
    async def handle_wallet(client: Client, message: Message):
        """Handle /wallet command."""
        telegram_id = message.from_user.id
        
        # Get user info from profile service (passed via closure or global)
        from database.db import get_db
        from bot.services.profile import ProfileService
        
        db = get_db()
        profile_service = ProfileService(db)
        
        user = await profile_service.get_user(telegram_id)
        
        if not user:
            await message.reply("❌ Please create a profile first using /start")
            return
        
        # Get transactions
        transactions = await wallet_service.get_transactions(user["id"], limit=10)
        
        # Format transactions
        if transactions:
            tx_lines = []
            for tx in transactions[:5]:
                amount = tx["amount"]
                sign = "+" if amount > 0 else ""
                tx_type = TRANSACTION_TYPES.get(tx["transaction_type"], tx["transaction_type"])
                tx_lines.append(f"{sign}{amount} 💰 - {tx_type}")
            
            tx_text = "\n".join(tx_lines)
        else:
            tx_text = NO_TRANSACTIONS
        
        text = WALLET_VIEW.format(
            balance=user.get("coins", 0),
            transactions=tx_text,
            referral_reward=REFERRAL_REWARD,
            filter_cost=FILTER_MATCH_COST,
        )
        
        await message.reply(text)
    
    @app.on_message(filters.regex(r"^💰 Wallet$") & filters.private)
    async def handle_wallet_button(client: Client, message: Message):
        """Handle wallet button from main menu."""
        await handle_wallet(client, message)
