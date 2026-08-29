"""
Moderation handlers for reports and blocks.
"""

from pyrogram import Client, filters
from pyrogram.types import Message


def register_moderation_handlers(app: Client, moderation_service):
    """Register moderation handlers."""
    
    @app.on_message(filters.command("report") & filters.private)
    async def handle_report_command(client: Client, message: Message):
        """Handle /report command."""
        await message.reply(
            "🚩 To report a user, use the Report button during an active chat.\n\n"
            "If you're not in a chat, you can't report anyone."
        )
    
    @app.on_message(filters.command("block") & filters.private)
    async def handle_block_command(client: Client, message: Message):
        """Handle /block command."""
        await message.reply(
            "🚫 To block a user, use the Block button during an active chat.\n\n"
            "If you're not in a chat, you can't block anyone directly."
        )
    
    @app.on_message(filters.command("help") & filters.private)
    async def handle_help_command(client: Client, message: Message):
        """Handle /help command."""
        from bot.texts import HELP_TEXT
        
        await message.reply(HELP_TEXT)
    
    @app.on_message(filters.regex(r"^🛡️ Safety / Help$") & filters.private)
    async def handle_help_button(client: Client, message: Message):
        """Handle help button from main menu."""
        await handle_help_command(client, message)
    
    @app.on_message(filters.command("settings") & filters.private)
    async def handle_settings_command(client: Client, message: Message):
        """Handle /settings command."""
        from bot.texts import SETTINGS_TEXT
        
        await message.reply(SETTINGS_TEXT)
    
    @app.on_message(filters.regex(r"^⚙️ Settings$") & filters.private)
    async def handle_settings_button(client: Client, message: Message):
        """Handle settings button from main menu."""
        await handle_settings_command(client, message)
