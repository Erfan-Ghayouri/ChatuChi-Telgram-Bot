"""
Matchmaking handlers for finding and connecting users.
"""

from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup
from bot.texts import (
    FINDING_TEXT, MATCH_FOUND_TEXT, RANDOM_MATCH_START,
    FILTER_MENU_TEXT, FILTER_OPTIONS, FILTER_COST_WARNING,
    INSUFFICIENT_COINS, MATCH_FILTERS
)
from bot.keyboards.chat import get_connected_keyboard


def register_matchmaking_handlers(app: Client, matchmaking_service, profile_service):
    """Register matchmaking handlers."""
    
    @app.on_message(filters.command("random") & filters.private)
    async def handle_random_match(client: Client, message: Message):
        """Handle /random command for free random matching."""
        telegram_id = message.from_user.id
        
        # Check if user is registered
        user = await profile_service.get_user(telegram_id)
        if not user:
            await message.reply("❌ Please create a profile first using /start")
            return
        
        # Check if already connected
        is_connected = await matchmaking_service.is_user_connected(telegram_id)
        if is_connected:
            await message.reply("❌ You're already in a chat. Use /stop to end it.")
            return
        
        # Check if already in queue
        in_queue = await matchmaking_service.is_user_in_queue(telegram_id)
        if in_queue:
            await message.reply("❌ You're already in the matchmaking queue.")
            return
        
        # Add to queue (random match is free)
        await matchmaking_service.add_to_queue(telegram_id, mode="random")
        
        await message.reply(
            RANDOM_MATCH_START,
            reply_markup=ReplyKeyboardMarkup(
                [["❌ Cancel Search"]],
                resize_keyboard=True
            )
        )
    
    @app.on_message(filters.command("find") & filters.private)
    async def handle_find_command(client: Client, message: Message):
        """Handle /find command to show filter options."""
        telegram_id = message.from_user.id
        
        user = await profile_service.get_user(telegram_id)
        if not user:
            await message.reply("❌ Please create a profile first using /start")
            return
        
        await message.reply(
            FILTER_MENU_TEXT,
            reply_markup=ReplyKeyboardMarkup(
                [
                    ["Sex: Anyone", "Sex: Male", "Sex: Female"],
                    ["City: Any", "Select City"],
                    ["🚀 Start Filtered Match (1 coin)"],
                    ["🔙 Back"],
                ],
                resize_keyboard=True
            )
        )
    
    @app.on_message(filters.regex(r"^🎯 Find Someone$") & filters.private)
    async def handle_find_button(client: Client, message: Message):
        """Handle find someone button from main menu."""
        await handle_find_command(client, message)
    
    @app.on_message(filters.regex(r"^⚡ Random Match$") & filters.private)
    async def handle_random_button(client: Client, message: Message):
        """Handle random match button from main menu."""
        await handle_random_match(client, message)
    
    @app.on_message(filters.regex(r"^🔎 Filters$") & filters.private)
    async def handle_filters_button(client: Client, message: Message):
        """Handle filters button from main menu."""
        await handle_find_command(client, message)
    
    @app.on_message(filters.regex(r"^🚀 Start Filtered Match \(1 coin\)$") & filters.private)
    async def handle_filtered_match(client: Client, message: Message):
        """Start filtered matchmaking (costs 1 coin on successful connection)."""
        telegram_id = message.from_user.id
        
        user = await profile_service.get_user(telegram_id)
        if not user:
            await message.reply("❌ Please create a profile first using /start")
            return
        
        # Check balance
        if user.get("coins", 0) < 1:
            await message.reply(
                INSUFFICIENT_COINS.format(coins=user.get("coins", 0))
            )
            return
        
        # Check if already connected
        is_connected = await matchmaking_service.is_user_connected(telegram_id)
        if is_connected:
            await message.reply("❌ You're already in a chat.")
            return
        
        # Get filters from state or use defaults
        from bot.states.registration import RegistrationStates
        state = await RegistrationStates.get_state(telegram_id)
        
        sex_filter = state.get("sex_filter", "any") if state else "any"
        city_filter = state.get("city_filter", "any") if state else "any"
        
        # Show finding message
        finding_text = FINDING_TEXT.format(
            sex_filter=MATCH_FILTERS.get(f"any_{sex_filter}", sex_filter),
            city_filter=MATCH_FILTERS.get(f"any_{city_filter}", city_filter)
        )
        
        await message.reply(finding_text)
        
        # Add to queue with filters (coin will be charged on successful match)
        success = await matchmaking_service.add_to_queue(
            telegram_id,
            mode="filtered",
            sex_filter=sex_filter if sex_filter != "any" else None,
            city_filter=city_filter if city_filter != "any" else None,
        )
        
        if not success:
            await message.reply("❌ Error joining queue. Please try again.")
            return
        
        await message.reply(
            "⏳ Waiting for a match...",
            reply_markup=ReplyKeyboardMarkup(
                [["❌ Cancel Search"]],
                resize_keyboard=True
            )
        )
    
    @app.on_message(filters.regex(r"^Sex: Anyone$") & filters.private)
    async def handle_sex_anyone(client: Client, message: Message):
        """Set sex filter to anyone."""
        telegram_id = message.from_user.id
        from bot.states.registration import RegistrationStates
        
        state = await RegistrationStates.get_state(telegram_id) or {}
        state["sex_filter"] = "any"
        await RegistrationStates.set_state(telegram_id, state)
        
        await message.reply("✅ Sex filter set to: Anyone")
    
    @app.on_message(filters.regex(r"^Sex: Male$") & filters.private)
    async def handle_sex_male(client: Client, message: Message):
        """Set sex filter to male."""
        telegram_id = message.from_user.id
        from bot.states.registration import RegistrationStates
        
        state = await RegistrationStates.get_state(telegram_id) or {}
        state["sex_filter"] = "male"
        await RegistrationStates.set_state(telegram_id, state)
        
        await message.reply("✅ Sex filter set to: Male")
    
    @app.on_message(filters.regex(r"^Sex: Female$") & filters.private)
    async def handle_sex_female(client: Client, message: Message):
        """Set sex filter to female."""
        telegram_id = message.from_user.id
        from bot.states.registration import RegistrationStates
        
        state = await RegistrationStates.get_state(telegram_id) or {}
        state["sex_filter"] = "female"
        await RegistrationStates.set_state(telegram_id, state)
        
        await message.reply("✅ Sex filter set to: Female")
    
    @app.on_message(filters.regex(r"^City: Any$") & filters.private)
    async def handle_city_any(client: Client, message: Message):
        """Set city filter to any."""
        telegram_id = message.from_user.id
        from bot.states.registration import RegistrationStates
        
        state = await RegistrationStates.get_state(telegram_id) or {}
        state["city_filter"] = "any"
        await RegistrationStates.set_state(telegram_id, state)
        
        await message.reply("✅ City filter set to: Any City")
    
    @app.on_message(filters.regex(r"^Select City$") & filters.private)
    async def handle_select_city(client: Client, message: Message):
        """Prompt to select city."""
        from bot.keyboards.main import get_province_keyboard
        
        await message.reply(
            "🏙️ Select your province first:",
            reply_markup=get_province_keyboard()
        )
    
    @app.on_message(filters.regex(r"^❌ Cancel Search$") & filters.private)
    async def handle_cancel_search(client: Client, message: Message):
        """Cancel matchmaking search."""
        telegram_id = message.from_user.id
        
        removed = await matchmaking_service.remove_from_queue(telegram_id)
        
        if removed:
            await message.reply(
                "❌ Search cancelled.",
                reply_markup=ReplyKeyboardMarkup(
                    [
                        ["🎯 Find Someone", "⚡ Random Match"],
                        ["🔙 Back to Menu"],
                    ],
                    resize_keyboard=True
                )
            )
        else:
            await message.reply("You weren't in the search queue.")
    
    @app.on_message(filters.regex(r"^🔙 Back$") & filters.private)
    async def handle_back(client: Client, message: Message):
        """Go back to main menu."""
        from bot.keyboards.main import get_main_menu_keyboard
        
        await message.reply(
            "🔙 Back to main menu.",
            reply_markup=get_main_menu_keyboard()
        )
    
    @app.on_message(filters.command("stop") & filters.private)
    async def handle_stop(client: Client, message: Message):
        """Stop current chat or leave queue."""
        telegram_id = message.from_user.id
        
        # Try to remove from queue first
        removed = await matchmaking_service.remove_from_queue(telegram_id)
        
        if removed:
            await message.reply("✅ Left the matchmaking queue.")
            return
        
        # Try to end active connection
        ended = await matchmaking_service.end_connection(telegram_id)
        
        if ended:
            await message.reply("✅ Chat ended.")
        else:
            await message.reply("❌ You're not in a chat or queue.")
