"""
Likes command handlers.
"""

from pyrogram import Client, filters
from pyrogram.types import Message
from bot.texts import LIKES_INFO


def register_likes_handlers(app: Client, profile_service):
    """Register likes handlers."""
    
    @app.on_message(filters.command("likes") & filters.private)
    async def handle_likes(client: Client, message: Message):
        """Handle /likes command."""
        telegram_id = message.from_user.id
        
        user = await profile_service.get_user(telegram_id)
        
        if not user:
            await message.reply("❌ Please create a profile first using /start")
            return
        
        text = LIKES_INFO.format(
            received=user.get("likes_received", 0),
            given=user.get("likes_given", 0),
        )
        
        await message.reply(text)
    
    @app.on_message(filters.regex(r"^❤️ Likes$") & filters.private)
    async def handle_likes_button(client: Client, message: Message):
        """Handle likes button from main menu."""
        await handle_likes(client, message)
