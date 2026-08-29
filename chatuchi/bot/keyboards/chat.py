"""
Chat keyboard for connected users.
"""

from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton


def get_connected_keyboard() -> ReplyKeyboardMarkup:
    """Get keyboard for connected chat."""
    keyboard = [
        ["❌ End Chat"],
        ["🚫 Block", "🚩 Report"],
        ["❤️ Like", "👤 View Profile"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_end_chat_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard shown after chat ends."""
    keyboard = [
        [InlineKeyboardButton("❤️ Like this person", callback_data="like_partner")],
        [InlineKeyboardButton("🚫 Block this person", callback_data="block_partner")],
        [InlineKeyboardButton("🎯 Find Someone New", callback_data="find_again")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_report_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for reporting reasons."""
    keyboard = [
        [InlineKeyboardButton("📢 Spam", callback_data="report_spam")],
        [InlineKeyboardButton("😠 Harassment", callback_data="report_harassment")],
        [InlineKeyboardButton("🔞 Inappropriate", callback_data="report_inappropriate")],
        [InlineKeyboardButton("💰 Scam", callback_data="report_scam")],
        [InlineKeyboardButton("📝 Other", callback_data="report_other")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_block_confirm_keyboard(blocked_user_id: int) -> InlineKeyboardMarkup:
    """Get keyboard for block confirmation."""
    keyboard = [
        [
            InlineKeyboardButton("Yes, Block", callback_data=f"confirm_block_{blocked_user_id}"),
            InlineKeyboardButton("Cancel", callback_data="cancel_block"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
