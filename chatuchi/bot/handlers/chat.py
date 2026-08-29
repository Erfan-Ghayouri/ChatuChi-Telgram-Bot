"""
Chat message handlers for relaying messages between connected users.
"""

from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup
from bot.keyboards.main import get_main_menu_keyboard
from bot.keyboards.chat import get_connected_keyboard, get_end_chat_keyboard


def register_chat_handlers(app: Client, relay_service, matchmaking_service):
    """Register chat message handlers."""
    
    @app.on_message(filters.private & ~filters.command)
    async def handle_private_message(client: Client, message: Message):
        """Handle private messages - relay if in active chat."""
        telegram_id = message.from_user.id
        
        # Check if user is in an active connection
        partner = await matchmaking_service.get_partner(telegram_id)
        
        if not partner:
            return  # Not in a chat, ignore
        
        # Get the partner's Telegram ID
        partner_telegram_id = partner["telegram_user_id"]
        
        # Relay the message
        try:
            success = await relay_service.relay_message(telegram_id, message)
            if not success:
                # End the connection on failure
                await matchmaking_service.end_connection(telegram_id)
                try:
                    await client.send_message(
                        partner_telegram_id,
                        "⚠️ Your partner's connection was lost.",
                        reply_markup=get_main_menu_keyboard()
                    )
                except Exception:
                    pass
        except Exception as e:
            # Handle relay errors
            await message.reply(f"⚠️ Error sending message: {str(e)}")
            
            # End the connection on error
            await matchmaking_service.end_connection(telegram_id)
            try:
                await client.send_message(
                    partner_telegram_id,
                    "⚠️ Your partner's connection was lost.",
                    reply_markup=get_main_menu_keyboard()
                )
            except Exception:
                pass
    
    @app.on_message(filters.regex(r"^❌ End Chat$") & filters.private)
    async def handle_end_chat(client: Client, message: Message):
        """Handle end chat button."""
        telegram_id = message.from_user.id
        
        partner = await matchmaking_service.get_partner(telegram_id)
        
        if not partner:
            await message.reply("❌ No active chat to end.")
            return
        
        # Get partner info
        partner_telegram_id = partner["telegram_user_id"]
        
        # End the connection
        await matchmaking_service.end_connection(telegram_id)
        
        # Notify both users
        await message.reply(
            "👋 Chat ended.\n\nWould you like to:",
            reply_markup=get_end_chat_keyboard()
        )
        
        try:
            await client.send_message(
                partner_telegram_id,
                "🚪 Your partner ended the chat.\n\nWould you like to:",
                reply_markup=get_end_chat_keyboard()
            )
        except Exception:
            pass  # Partner may have blocked the bot
    
    @app.on_message(filters.regex(r"^🚫 Block$") & filters.private)
    async def handle_block_request(client: Client, message: Message):
        """Handle block request."""
        telegram_id = message.from_user.id
        
        partner = await matchmaking_service.get_partner(telegram_id)
        
        if not partner:
            await message.reply("❌ No active chat.")
            return
        
        # Get partner info
        partner_telegram_id = partner["telegram_user_id"]
        
        # Store blocked user ID in state for confirmation
        from bot.states.registration import RegistrationStates
        await RegistrationStates.set_state(telegram_id, {
            "step": "confirming_block",
            "blocking_user_id": partner_telegram_id
        })
        
        await message.reply(
            "🚫 Are you sure you want to block this user?\n\n"
            "You will never be matched with them again.",
            reply_markup=ReplyKeyboardMarkup(
                [
                    ["✅ Yes, Block"],
                    ["❌ Cancel"],
                ],
                resize_keyboard=True
            )
        )
    
    @app.on_message(filters.regex(r"^✅ Yes, Block$") & filters.private)
    async def handle_confirm_block(client: Client, message: Message):
        """Confirm blocking a user."""
        telegram_id = message.from_user.id
        
        from bot.states.registration import RegistrationStates
        state = await RegistrationStates.get_state(telegram_id)
        
        if not state or state.get("step") != "confirming_block":
            await message.reply("❌ No block action to confirm.")
            return
        
        partner_id = state.get("blocking_user_id")
        
        if partner_id:
            # Add block
            from database.db import get_db
            from database.repositories.blocks import BlocksRepository
            
            db = get_db()
            blocks_repo = BlocksRepository(db)
            
            await blocks_repo.add_block(telegram_id, partner_id)
            
            # End connection
            await matchmaking_service.end_connection(telegram_id)
            
            await message.reply(
                "🚫 User blocked successfully.",
                reply_markup=get_main_menu_keyboard()
            )
        
        await RegistrationStates.clear_state(telegram_id)
    
    @app.on_message(filters.regex(r"^❌ Cancel$") & filters.private)
    async def handle_cancel_action(client: Client, message: Message):
        """Cancel current action."""
        telegram_id = message.from_user.id
        
        from bot.states.registration import RegistrationStates
        await RegistrationStates.clear_state(telegram_id)
        
        # Check if in a chat
        partner = await matchmaking_service.get_partner(telegram_id)
        
        if partner:
            await message.reply(
                "❌ Cancelled.",
                reply_markup=get_connected_keyboard()
            )
        else:
            await message.reply(
                "❌ Cancelled.",
                reply_markup=get_main_menu_keyboard()
            )
    
    @app.on_message(filters.regex(r"^🚩 Report$") & filters.private)
    async def handle_report_request(client: Client, message: Message):
        """Handle report request."""
        telegram_id = message.from_user.id
        
        partner = await matchmaking_service.get_partner(telegram_id)
        
        if not partner:
            await message.reply("❌ No active chat.")
            return
        
        # Get partner info
        partner_telegram_id = partner["telegram_user_id"]
        
        # Store reported user ID in state
        from bot.states.registration import RegistrationStates
        await RegistrationStates.set_state(telegram_id, {
            "step": "selecting_report_reason",
            "reporting_user_id": partner_telegram_id
        })
        
        from bot.keyboards.chat import get_report_keyboard
        await message.reply(
            "🚩 Why are you reporting this user?",
            reply_markup=get_report_keyboard()
        )
    
    @app.on_callback_query(filters.regex(r"^report_"))
    async def handle_report_callback(client, callback_query):
        """Handle report reason selection."""
        telegram_id = callback_query.from_user.id
        
        from bot.states.registration import RegistrationStates
        state = await RegistrationStates.get_state(telegram_id)
        
        if not state or state.get("step") != "selecting_report_reason":
            await callback_query.answer("No report in progress.", show_alert=True)
            return
        
        reason_map = {
            "report_spam": "spam",
            "report_harassment": "harassment",
            "report_inappropriate": "inappropriate",
            "report_scam": "scam",
            "report_other": "other",
        }
        
        reason = reason_map.get(callback_query.data)
        if not reason:
            await callback_query.answer("Invalid reason.", show_alert=True)
            return
        
        partner_id = state.get("reporting_user_id")
        
        if partner_id:
            # Submit report
            from database.db import get_db
            from database.repositories.reports import ReportsRepository
            
            db = get_db()
            reports_repo = ReportsRepository(db)
            
            await reports_repo.submit_report(
                reporter_id=telegram_id,
                reported_id=partner_id,
                reason=reason,
            )
            
            await callback_query.message.edit_text(
                "✅ Report submitted.\n\nThank you for helping keep ChatuChi safe."
            )
        
        await RegistrationStates.clear_state(telegram_id)
    
    @app.on_message(filters.regex(r"^❤️ Like$") & filters.private)
    async def handle_like_request(client: Client, message: Message):
        """Handle like request."""
        telegram_id = message.from_user.id
        
        partner = await matchmaking_service.get_partner(telegram_id)
        
        if not partner:
            await message.reply("❌ No active chat.")
            return
        
        # Get partner info
        partner_telegram_id = partner["telegram_user_id"]
        
        # Send like
        from database.db import get_db
        from database.repositories.likes import LikesRepository
        
        db = get_db()
        likes_repo = LikesRepository(db)
        
        try:
            await likes_repo.add_like(telegram_id, partner_telegram_id)
            await message.reply("❤️ You liked this person!")
        except Exception as e:
            if "UNIQUE constraint" in str(e):
                await message.reply("You already liked this person.")
            else:
                await message.reply("❌ Error sending like.")
    
    @app.on_message(filters.regex(r"^👤 View Profile$") & filters.private)
    async def handle_view_partner_profile(client: Client, message: Message):
        """View partner's anonymous profile."""
        telegram_id = message.from_user.id
        
        partner = await matchmaking_service.get_partner(telegram_id)
        
        if not partner:
            await message.reply("❌ No active chat.")
            return
        
        # Get partner's profile service
        from bot.services.profile import ProfileService
        from database.db import get_db
        
        db = get_db()
        profile_service = ProfileService(db)
        
        partner_data = await profile_service.get_user(partner["telegram_user_id"])
        
        if partner_data:
            from bot.texts import PROFILE_VIEW
            text = PROFILE_VIEW.format(
                name=partner_data["name"],
                age=partner_data["age"],
                sex=partner_data["sex"],
                city=partner_data.get("city", "Not specified"),
                bio=partner_data.get("bio", "No bio"),
                likes=partner_data.get("likes_received", 0),
                public_id=partner_data["public_id"],
            )
            await message.reply(text)
        else:
            await message.reply("❌ Could not retrieve partner's profile.")
    
    @app.on_callback_query(filters.regex(r"^like_partner$"))
    async def handle_like_partner_callback(client, callback_query):
        """Handle like partner after chat ends."""
        telegram_id = callback_query.from_user.id
        
        # Get recent connection
        from database.db import get_db
        from database.repositories.connections import ConnectionsRepository
        from database.repositories.likes import LikesRepository
        
        db = get_db()
        connections_repo = ConnectionsRepository(db)
        likes_repo = LikesRepository(db)
        
        # Find most recent connection
        recent = await connections_repo.get_recent_for_user(telegram_id)
        
        if not recent:
            await callback_query.answer("No recent chat found.", show_alert=True)
            return
        
        # Get partner
        partner_id = recent["user_b"] if recent["user_a"] == telegram_id else recent["user_a"]
        
        try:
            await likes_repo.add_like(telegram_id, partner_id)
            await callback_query.answer("❤️ Like sent!", show_alert=True)
        except Exception as e:
            if "UNIQUE constraint" in str(e):
                await callback_query.answer("You already liked this person.", show_alert=True)
            else:
                await callback_query.answer("Error sending like.", show_alert=True)
    
    @app.on_callback_query(filters.regex(r"^block_partner$"))
    async def handle_block_partner_callback(client, callback_query):
        """Handle block partner after chat ends."""
        telegram_id = callback_query.from_user.id
        
        from database.db import get_db
        from database.repositories.connections import ConnectionsRepository
        from database.repositories.blocks import BlocksRepository
        
        db = get_db()
        connections_repo = ConnectionsRepository(db)
        blocks_repo = BlocksRepository(db)
        
        # Find most recent connection
        recent = await connections_repo.get_recent_for_user(telegram_id)
        
        if not recent:
            await callback_query.answer("No recent chat found.", show_alert=True)
            return
        
        # Get partner
        partner_id = recent["user_b"] if recent["user_a"] == telegram_id else recent["user_a"]
        
        await blocks_repo.add_block(telegram_id, partner_id)
        
        await callback_query.answer("🚫 User blocked.", show_alert=True)
        await callback_query.message.edit_text(
            "🚫 User blocked successfully.",
            reply_markup=get_main_menu_keyboard()
        )
    
    @app.on_callback_query(filters.regex(r"^find_again$"))
    async def handle_find_again_callback(client, callback_query):
        """Handle find someone new after chat ends."""
        telegram_id = callback_query.from_user.id
        
        await callback_query.message.edit_text(
            "🔎 Finding someone...",
            reply_markup=get_main_menu_keyboard()
        )
        
        # Trigger random match
        from bot.services.matchmaking import MatchmakingService
        from database.db import get_db
        
        db = get_db()
        matchmaking_service = MatchmakingService(db)
        
        await matchmaking_service.add_to_queue(telegram_id, mode="random")
    
    @app.on_callback_query(filters.regex(r"^main_menu$"))
    async def handle_main_menu_callback(client, callback_query):
        """Return to main menu."""
        await callback_query.message.edit_text(
            "🏠 Back to main menu.",
            reply_markup=get_main_menu_keyboard()
        )
