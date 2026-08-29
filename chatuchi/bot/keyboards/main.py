"""
Main menu keyboards.
"""

from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from bot.texts import MAIN_MENU_BUTTONS, SEX_OPTIONS, SKIP_BUTTON, BACK_BUTTON, CANCEL_BUTTON


def main_keyboard() -> ReplyKeyboardMarkup:
    """Create main menu keyboard."""
    keyboard = [
        [
            KeyboardButton(MAIN_MENU_BUTTONS["find"]),
            KeyboardButton(MAIN_MENU_BUTTONS["random"]),
        ],
        [
            KeyboardButton(MAIN_MENU_BUTTONS["filters"]),
            KeyboardButton(MAIN_MENU_BUTTONS["profile"]),
        ],
        [
            KeyboardButton(MAIN_MENU_BUTTONS["wallet"]),
            KeyboardButton(MAIN_MENU_BUTTONS["likes"]),
        ],
        [
            KeyboardButton(MAIN_MENU_BUTTONS["invite"]),
            KeyboardButton(MAIN_MENU_BUTTONS["settings"]),
        ],
        [
            KeyboardButton(MAIN_MENU_BUTTONS["help"]),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, persistent=True)


def welcome_keyboard() -> InlineKeyboardMarkup:
    """Create welcome screen keyboard."""
    keyboard = [
        [InlineKeyboardButton("🎯 Create Profile", callback_data="create_profile")],
        [InlineKeyboardButton("❓ Help & Safety", callback_data="help_safety")],
    ]
    return InlineKeyboardMarkup(keyboard)


def sex_selection_keyboard() -> InlineKeyboardMarkup:
    """Create sex selection keyboard."""
    keyboard = [
        [InlineKeyboardButton(SEX_OPTIONS["male"], callback_data="sex_male")],
        [InlineKeyboardButton(SEX_OPTIONS["female"], callback_data="sex_female")],
        [InlineKeyboardButton(SEX_OPTIONS["other"], callback_data="sex_other")],
    ]
    return InlineKeyboardMarkup(keyboard)


def cancel_keyboard() -> ReplyKeyboardMarkup:
    """Create keyboard with just cancel button."""
    keyboard = [[KeyboardButton(CANCEL_BUTTON)]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def back_keyboard() -> ReplyKeyboardMarkup:
    """Create keyboard with back button."""
    keyboard = [[KeyboardButton(BACK_BUTTON)]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def skip_back_keyboard() -> ReplyKeyboardMarkup:
    """Create keyboard with skip and back buttons."""
    keyboard = [
        [KeyboardButton(SKIP_BUTTON), KeyboardButton(BACK_BUTTON)],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_start_keyboard():
    """Get start menu keyboard (deprecated, use welcome_keyboard)."""
    return welcome_keyboard()


def get_main_menu_keyboard():
    """Get main menu keyboard."""
    return main_keyboard()


def get_gender_keyboard():
    """Get gender selection keyboard."""
    keyboard = [
        ["👨 Male"],
        ["👩 Female"],
        ["🌐 Other"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


def get_province_keyboard():
    """Get province selection keyboard."""
    from bot.utils.helpers import load_cities_data
    cities_data = load_cities_data()
    
    provinces = sorted(cities_data.keys())[:20]  # Limit to first 20 for usability
    buttons = []
    
    for i in range(0, len(provinces), 2):
        row = [provinces[i]]
        if i + 1 < len(provinces):
            row.append(provinces[i + 1])
        buttons.append(row)
    
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)
