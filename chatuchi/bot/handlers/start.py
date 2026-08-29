"""
Start command and registration flow handlers.
"""

from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup
from bot.keyboards.main import get_start_keyboard, get_main_menu_keyboard
from bot.states.registration import RegistrationStates
from bot.texts import WELCOME_TEXT, REGISTRATION_STEPS
from database.db import get_db


def register_start_handlers(app: Client, profile_service):
    """Register start command handlers."""
    
    @app.on_message(filters.command("start") & filters.private)
    async def handle_start(client: Client, message: Message):
        """Handle /start command."""
        telegram_id = message.from_user.id
        
        # Check if user has a referral code in start parameter
        referrer_public_id = None
        if len(message.command) > 1:
            ref_param = message.command[1]
            if ref_param.startswith("ref_"):
                referrer_public_id = ref_param[4:]  # Remove "ref_" prefix
        
        # Check if user is already registered
        user = await profile_service.get_user(telegram_id)
        
        if user:
            # User is registered, show main menu
            keyboard = get_main_menu_keyboard()
            await message.reply(
                f"👋 Welcome back, {user['name']}!",
                reply_markup=keyboard
            )
            return
        
        # New user, start registration
        state_data = {
            "step": "welcome",
            "referrer_public_id": referrer_public_id
        }
        await RegistrationStates.set_state(telegram_id, state_data)
        
        keyboard = ReplyKeyboardMarkup(
            [["✅ Create Profile"]],
            resize_keyboard=True
        )
        
        await message.reply(
            WELCOME_TEXT,
            reply_markup=keyboard
        )
    
    @app.on_message(filters.regex(r"^✅ Create Profile$") & filters.private)
    async def handle_create_profile(client: Client, message: Message):
        """Handle create profile button."""
        telegram_id = message.from_user.id
        state = await RegistrationStates.get_state(telegram_id)
        
        if not state:
            await message.reply("Please use /start to begin registration.")
            return
        
        # Move to name step
        state["step"] = "asking_name"
        await RegistrationStates.set_state(telegram_id, state)
        
        await message.reply(
            "📝 What should we call you?\n\n"
            "Enter your display name (this will be shown to other users):"
        )
    
    @app.on_message(filters.private)
    async def handle_registration_flow(client: Client, message: Message):
        """Handle registration state machine."""
        telegram_id = message.from_user.id
        state = await RegistrationStates.get_state(telegram_id)
        
        if not state:
            return  # Not in registration
        
        step = state.get("step")
        
        if step == "asking_name":
            name = message.text.strip()
            if len(name) < 2 or len(name) > 50:
                await message.reply("Please enter a valid name (2-50 characters).")
                return
            
            state["name"] = name
            state["step"] = "asking_age"
            await RegistrationStates.set_state(telegram_id, state)
            
            await message.reply(
                "🎂 How old are you?\n\n"
                "⚠️ You must be 18 or older to use this service.\n"
                "Enter your age:"
            )
        
        elif step == "asking_age":
            try:
                age = int(message.text.strip())
            except ValueError:
                await message.reply("Please enter a valid number for your age.")
                return
            
            if age < 18:
                await message.reply(
                    "❌ Sorry, you must be at least 18 years old to use ChatuChi.\n\n"
                    "Thank you for your interest!"
                )
                await RegistrationStates.clear_state(telegram_id)
                return
            
            state["age"] = age
            state["step"] = "asking_sex"
            await RegistrationStates.set_state(telegram_id, state)
            
            from bot.keyboards.main import get_gender_keyboard
            keyboard = get_gender_keyboard()
            
            await message.reply(
                "⚤ What is your sex?",
                reply_markup=keyboard
            )
        
        elif step == "asking_sex":
            sex = message.text.strip()
            if sex not in ["Male", "Female", "Other"]:
                await message.reply("Please select one of the options below.")
                return
            
            state["sex"] = sex
            state["step"] = "asking_city"
            await RegistrationStates.set_state(telegram_id, state)
            
            from bot.keyboards.main import get_province_keyboard
            keyboard = get_province_keyboard()
            
            await message.reply(
                "🏙️ Select your province:",
                reply_markup=keyboard
            )
        
        elif step == "asking_province":
            province = message.text.strip()
            from bot.utils.helpers import load_cities_data
            cities_data = load_cities_data()
            
            if province not in cities_data:
                await message.reply("Please select a valid province from the list.")
                return
            
            state["province"] = province
            state["step"] = "asking_city"
            await RegistrationStates.set_state(telegram_id, state)
            
            keyboard = get_city_keyboard(province)
            
            await message.reply(
                f"🏙️ Select your city in {province}:",
                reply_markup=keyboard
            )
        
        elif step == "asking_city":
            city = message.text.strip()
            state["city"] = city
            state["step"] = "asking_bio"
            await RegistrationStates.set_state(telegram_id, state)
            
            await message.reply(
                "📝 Write a short bio about yourself:\n\n"
                "This will be shown to other users. Keep it friendly and appropriate!\n\n"
                "Send 'Skip' to skip this step."
            )
        
        elif step == "asking_bio":
            bio = message.text.strip()
            if bio.lower() == "skip":
                bio = ""
            
            state["bio"] = bio
            state["step"] = "completing"
            await RegistrationStates.set_state(telegram_id, state)
            
            # Create the profile
            referrer_id = state.get("referrer_public_id")
            
            try:
                user = await profile_service.create_profile(
                    telegram_user_id=telegram_id,
                    name=state["name"],
                    age=state["age"],
                    sex=state["sex"],
                    city=state["city"],
                    bio=bio,
                    referrer_public_id=referrer_id,
                )
                
                # Handle referral reward
                if referrer_id:
                    from bot.services.referral import ReferralService
                    from database.db import get_db
                    db = get_db()
                    referral_service = ReferralService(db)
                    await referral_service.process_referral(referrer_id, telegram_id)
                
                await message.reply(
                    f"🎉 Profile created successfully!\n\n"
                    f"🆔 Your ChatuChi ID: `{user['public_id']}`\n"
                    f"💰 Starting balance: {user['coins']} coins\n\n"
                    "You can now start chatting with others!"
                )
                
                # Clear registration state
                await RegistrationStates.clear_state(telegram_id)
                
                # Show main menu
                keyboard = get_main_menu_keyboard()
                await message.reply(
                    "✨ Ready to meet someone new?",
                    reply_markup=keyboard
                )
                
            except Exception as e:
                await message.reply(
                    f"❌ Error creating profile: {str(e)}\n\n"
                    "Please try again with /start"
                )
                await RegistrationStates.clear_state(telegram_id)
        
        else:
            # Unknown step, clear state
            await RegistrationStates.clear_state(telegram_id)


def get_city_keyboard(province: str):
    """Get city selection keyboard for a province."""
    from bot.utils.helpers import load_cities_data
    cities_data = load_cities_data()
    
    cities = cities_data.get(province, [])
    buttons = []
    
    for i in range(0, len(cities), 2):
        row = [cities[i]]
        if i + 1 < len(cities):
            row.append(cities[i + 1])
        buttons.append(row)
    
    buttons.append(["◀️ Back to Provinces"])
    
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def get_province_keyboard():
    """Get province selection keyboard."""
    from bot.utils.helpers import load_cities_data
    cities_data = load_cities_data()
    
    provinces = sorted(cities_data.keys())
    buttons = []
    
    for i in range(0, len(provinces), 2):
        row = [provinces[i]]
        if i + 1 < len(provinces):
            row.append(provinces[i + 1])
        buttons.append(row)
    
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)
