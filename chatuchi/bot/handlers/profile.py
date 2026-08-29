"""
Profile command handlers.
"""

from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup
from bot.texts import MY_PROFILE_VIEW, PROFILE_EDIT_MENU, EDIT_OPTIONS
from bot.keyboards.main import get_main_menu_keyboard


def register_profile_handlers(app: Client, profile_service):
    """Register profile handlers."""
    
    @app.on_message(filters.command("profile") & filters.private)
    async def handle_view_profile(client: Client, message: Message):
        """Handle /profile command to view own profile."""
        telegram_id = message.from_user.id
        
        user = await profile_service.get_user(telegram_id)
        
        if not user:
            await message.reply("❌ Please create a profile first using /start")
            return
        
        # Check if viewing another user's profile via public ID
        if len(message.command) > 1:
            public_id = message.command[1]
            target_user = await profile_service.get_user_by_public_id(public_id)
            
            if target_user:
                from bot.texts import PROFILE_VIEW
                text = PROFILE_VIEW.format(
                    name=target_user["name"],
                    age=target_user["age"],
                    sex=target_user["sex"],
                    city=target_user.get("city", "Not specified"),
                    bio=target_user.get("bio", "No bio"),
                    likes=target_user.get("likes_received", 0),
                    public_id=target_user["public_id"],
                )
                await message.reply(text)
            else:
                await message.reply(f"❌ User with ID {public_id} not found.")
            return
        
        # Show own profile
        text = MY_PROFILE_VIEW.format(
            name=user["name"],
            age=user["age"],
            sex=user["sex"],
            city=user.get("city", "Not specified"),
            bio=user.get("bio", "No bio"),
            likes_received=user.get("likes_received", 0),
            likes_given=user.get("likes_given", 0),
            coins=user.get("coins", 0),
            public_id=user["public_id"],
        )
        
        keyboard = ReplyKeyboardMarkup(
            [
                ["✏️ Edit Profile"],
                ["🔙 Back to Menu"],
            ],
            resize_keyboard=True
        )
        
        await message.reply(text, reply_markup=keyboard)
    
    @app.on_message(filters.regex(r"^✏️ Edit Profile$") & filters.private)
    async def handle_edit_profile_menu(client: Client, message: Message):
        """Show edit profile menu."""
        telegram_id = message.from_user.id
        
        user = await profile_service.get_user(telegram_id)
        if not user:
            await message.reply("❌ Please create a profile first using /start")
            return
        
        await message.reply(
            PROFILE_EDIT_MENU,
            reply_markup=ReplyKeyboardMarkup(
                [
                    ["✏️ Change Name", "🎂 Change Age"],
                    ["🔄 Change Sex", "🏙️ Change City"],
                    ["📝 Change Bio"],
                    ["🔙 Back to Menu"],
                ],
                resize_keyboard=True
            )
        )
    
    @app.on_message(filters.regex(r"^🔙 Back to Menu$") & filters.private)
    async def handle_back_to_menu(client: Client, message: Message):
        """Return to main menu."""
        await message.reply(
            "🏠 Back to main menu.",
            reply_markup=get_main_menu_keyboard()
        )
    
    @app.on_message(filters.regex(r"^✏️ Change Name$") & filters.private)
    async def handle_change_name(client: Client, message: Message):
        """Handle name change request."""
        telegram_id = message.from_user.id
        
        user = await profile_service.get_user(telegram_id)
        if not user:
            await message.reply("❌ Please create a profile first using /start")
            return
        
        await message.reply(
            "📝 Enter your new display name:",
            reply_markup=ReplyKeyboardMarkup([["❌ Cancel"]], resize_keyboard=True)
        )
        
        # Set state for name change
        from bot.states.registration import RegistrationStates
        await RegistrationStates.set_state(telegram_id, {"step": "changing_name"})
    
    @app.on_message(filters.regex(r"^🎂 Change Age$") & filters.private)
    async def handle_change_age(client: Client, message: Message):
        """Handle age change request."""
        telegram_id = message.from_user.id
        
        user = await profile_service.get_user(telegram_id)
        if not user:
            await message.reply("❌ Please create a profile first using /start")
            return
        
        await message.reply(
            "🎂 Enter your new age (must be 18+):",
            reply_markup=ReplyKeyboardMarkup([["❌ Cancel"]], resize_keyboard=True)
        )
        
        from bot.states.registration import RegistrationStates
        await RegistrationStates.set_state(telegram_id, {"step": "changing_age"})
    
    @app.on_message(filters.regex(r"^🔄 Change Sex$") & filters.private)
    async def handle_change_sex(client: Client, message: Message):
        """Handle sex change request."""
        telegram_id = message.from_user.id
        
        user = await profile_service.get_user(telegram_id)
        if not user:
            await message.reply("❌ Please create a profile first using /start")
            return
        
        keyboard = ReplyKeyboardMarkup(
            [
                ["👨 Male"],
                ["👩 Female"],
                ["🌐 Other"],
                ["❌ Cancel"],
            ],
            resize_keyboard=True
        )
        
        await message.reply("🔄 Select your sex:", reply_markup=keyboard)
        
        from bot.states.registration import RegistrationStates
        await RegistrationStates.set_state(telegram_id, {"step": "changing_sex"})
    
    @app.on_message(filters.regex(r"^🏙️ Change City$") & filters.private)
    async def handle_change_city(client: Client, message: Message):
        """Handle city change request."""
        telegram_id = message.from_user.id
        
        user = await profile_service.get_user(telegram_id)
        if not user:
            await message.reply("❌ Please create a profile first using /start")
            return
        
        from bot.keyboards.main import get_province_keyboard
        await message.reply(
            "🏙️ Select your province:",
            reply_markup=get_province_keyboard()
        )
        
        from bot.states.registration import RegistrationStates
        await RegistrationStates.set_state(telegram_id, {"step": "changing_province"})
    
    @app.on_message(filters.regex(r"^📝 Change Bio$") & filters.private)
    async def handle_change_bio(client: Client, message: Message):
        """Handle bio change request."""
        telegram_id = message.from_user.id
        
        user = await profile_service.get_user(telegram_id)
        if not user:
            await message.reply("❌ Please create a profile first using /start")
            return
        
        await message.reply(
            "📝 Enter your new bio (or 'Skip' to clear):",
            reply_markup=ReplyKeyboardMarkup([["❌ Cancel"]], resize_keyboard=True)
        )
        
        from bot.states.registration import RegistrationStates
        await RegistrationStates.set_state(telegram_id, {"step": "changing_bio"})
    
    @app.on_message(filters.regex(r"^❌ Cancel$") & filters.private)
    async def handle_cancel_edit(client: Client, message: Message):
        """Cancel edit operation."""
        telegram_id = message.from_user.id
        
        from bot.states.registration import RegistrationStates
        await RegistrationStates.clear_state(telegram_id)
        
        await message.reply(
            "❌ Edit cancelled.",
            reply_markup=get_main_menu_keyboard()
        )
    
    @app.on_message(filters.private)
    async def handle_profile_edit_input(client: Client, message: Message):
        """Handle input during profile editing."""
        telegram_id = message.from_user.id
        
        from bot.states.registration import RegistrationStates
        state = await RegistrationStates.get_state(telegram_id)
        
        if not state:
            return
        
        step = state.get("step")
        
        if step == "changing_name":
            name = message.text.strip()
            if len(name) < 2 or len(name) > 50:
                await message.reply("Please enter a valid name (2-50 characters).")
                return
            
            await profile_service.update_profile(telegram_id, name=name)
            await RegistrationStates.clear_state(telegram_id)
            await message.reply(
                "✅ Name updated successfully!",
                reply_markup=get_main_menu_keyboard()
            )
        
        elif step == "changing_age":
            try:
                age = int(message.text.strip())
            except ValueError:
                await message.reply("Please enter a valid number.")
                return
            
            if age < 18:
                await message.reply("❌ You must be at least 18 years old.")
                return
            
            await profile_service.update_profile(telegram_id, age=age)
            await RegistrationStates.clear_state(telegram_id)
            await message.reply(
                "✅ Age updated successfully!",
                reply_markup=get_main_menu_keyboard()
            )
        
        elif step == "changing_sex":
            sex_map = {
                "👨 Male": "Male",
                "👩 Female": "Female",
                "🌐 Other": "Other",
            }
            sex = sex_map.get(message.text.strip())
            
            if not sex:
                await message.reply("Please select a valid option.")
                return
            
            await profile_service.update_profile(telegram_id, sex=sex)
            await RegistrationStates.clear_state(telegram_id)
            await message.reply(
                "✅ Sex updated successfully!",
                reply_markup=get_main_menu_keyboard()
            )
        
        elif step in ["changing_province", "changing_city"]:
            # Handle province/city selection
            from bot.utils.helpers import load_cities_data
            cities_data = load_cities_data()
            
            if step == "changing_province":
                province = message.text.strip()
                if province not in cities_data:
                    await message.reply("Please select a valid province.")
                    return
                
                state["province"] = province
                state["step"] = "changing_city"
                await RegistrationStates.set_state(telegram_id, state)
                
                from bot.handlers.start import get_city_keyboard
                await message.reply(
                    f"🏙️ Select your city in {province}:",
                    reply_markup=get_city_keyboard(province)
                )
                return
            
            elif step == "changing_city":
                city = message.text.strip()
                await profile_service.update_profile(telegram_id, city=city)
                await RegistrationStates.clear_state(telegram_id)
                await message.reply(
                    "✅ City updated successfully!",
                    reply_markup=get_main_menu_keyboard()
                )
        
        elif step == "changing_bio":
            bio = message.text.strip()
            if bio.lower() == "skip":
                bio = ""
            
            await profile_service.update_profile(telegram_id, bio=bio)
            await RegistrationStates.clear_state(telegram_id)
            await message.reply(
                "✅ Bio updated successfully!",
                reply_markup=get_main_menu_keyboard()
            )
