"""
Referral command handlers.
"""

from pyrogram import Client, filters
from pyrogram.types import Message
from bot.texts import REFERRAL_INFO


def register_referral_handlers(app: Client, referral_service):
    """Register referral handlers."""
    
    @app.on_message(filters.command("invite") & filters.private)
    async def handle_invite(client: Client, message: Message):
        """Handle /invite command."""
        telegram_id = message.from_user.id
        
        from database.db import get_db
        from bot.services.profile import ProfileService
        
        db = get_db()
        profile_service = ProfileService(db)
        
        user = await profile_service.get_user(telegram_id)
        
        if not user:
            await message.reply("❌ Please create a profile first using /start")
            return
        
        # Generate referral link
        from config import BOT_USERNAME
        public_id = user["public_id"]
        referral_link = f"https://t.me/{BOT_USERNAME}?start=ref_{public_id}"
        
        # Get referral stats
        stats = await referral_service.get_referral_stats(user["id"])
        
        text = REFERRAL_INFO.format(
            link=referral_link,
            total=stats["total"],
            successful=stats["successful"],
            earned=stats["earned"],
            reward=1,  # REFERRAL_REWARD
        )
        
        await message.reply(text)
    
    @app.on_message(filters.regex(r"^🔗 Invite Friends$") & filters.private)
    async def handle_invite_button(client: Client, message: Message):
        """Handle invite button from main menu."""
        await handle_invite(client, message)
