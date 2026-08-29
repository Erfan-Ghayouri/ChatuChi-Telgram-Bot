"""
Admin command handlers.
"""

from pyrogram import Client, filters
from pyrogram.types import Message
from config import ADMIN_IDS


def register_admin_handlers(app: Client, moderation_service, profile_service):
    """Register admin handlers."""
    
    def is_admin(user_id: int) -> bool:
        """Check if user is an admin."""
        return user_id in ADMIN_IDS
    
    @app.on_message(filters.command("admin") & filters.private)
    async def handle_admin_panel(client: Client, message: Message):
        """Handle /admin command."""
        telegram_id = message.from_user.id
        
        if not is_admin(telegram_id):
            await message.reply("❌ Access denied.")
            return
        
        from bot.texts import ADMIN_PANEL
        
        # Get stats
        from database.db import get_db
        from database.repositories.users import UserRepository
        from database.repositories.queue import QueueRepository
        from database.repositories.connections import ConnectionsRepository
        from database.repositories.reports import ReportsRepository
        
        db = get_db()
        users_repo = UserRepository(db)
        queue_repo = QueueRepository(db)
        connections_repo = ConnectionsRepository(db)
        reports_repo = ReportsRepository(db)
        
        total_users = await users_repo.count_all()
        in_queue = await queue_repo.count_all()
        connected = await connections_repo.count_active()
        banned = await users_repo.count_banned()
        pending_reports = await reports_repo.count_pending()
        
        text = ADMIN_PANEL.format(
            total_users=total_users,
            online=total_users,  # Simplified
            in_queue=in_queue,
            connected=connected,
            banned=banned,
            pending_reports=pending_reports,
        )
        
        await message.reply(text)
    
    @app.on_message(filters.command("ban") & filters.private)
    async def handle_ban_command(client: Client, message: Message):
        """Handle /ban command."""
        telegram_id = message.from_user.id
        
        if not is_admin(telegram_id):
            await message.reply("❌ Access denied.")
            return
        
        from bot.texts import BAN_CONFIRM
        await message.reply(BAN_CONFIRM)
        
        # Set state for ban
        from bot.states.registration import RegistrationStates
        await RegistrationStates.set_state(telegram_id, {"step": "banning_user"})
    
    @app.on_message(filters.command("unban") & filters.private)
    async def handle_unban_command(client: Client, message: Message):
        """Handle /unban command."""
        telegram_id = message.from_user.id
        
        if not is_admin(telegram_id):
            await message.reply("❌ Access denied.")
            return
        
        from bot.texts import UNBAN_CONFIRM
        await message.reply(UNBAN_CONFIRM)
        
        from bot.states.registration import RegistrationStates
        await RegistrationStates.set_state(telegram_id, {"step": "unbanning_user"})
    
    @app.on_message(filters.command("user") & filters.private)
    async def handle_user_command(client: Client, message: Message):
        """Handle /user command to view user details."""
        telegram_id = message.from_user.id
        
        if not is_admin(telegram_id):
            await message.reply("❌ Access denied.")
            return
        
        if len(message.command) < 2:
            await message.reply("Usage: /user PUBLIC_ID")
            return
        
        public_id = message.command[1]
        user = await profile_service.get_user_by_public_id(public_id)
        
        if not user:
            await message.reply(f"❌ User {public_id} not found.")
            return
        
        from bot.texts import USER_ADMIN_VIEW
        from bot.utils.helpers import format_datetime
        
        text = USER_ADMIN_VIEW.format(
            public_id=user["public_id"],
            telegram_id=user["telegram_user_id"],
            name=user["name"],
            age=user["age"],
            sex=user["sex"],
            city=user.get("city", "Not specified"),
            coins=user.get("coins", 0),
            status=user.get("status", "offline"),
            is_banned="Yes" if user.get("is_banned") else "No",
            report_count=0,  # TODO: Get actual count
            created_at=format_datetime(user.get("created_at")),
            last_seen=format_datetime(user.get("last_seen")),
        )
        
        await message.reply(text)
    
    @app.on_message(filters.command("stats") & filters.private)
    async def handle_stats_command(client: Client, message: Message):
        """Handle /stats command."""
        telegram_id = message.from_user.id
        
        if not is_admin(telegram_id):
            await message.reply("❌ Access denied.")
            return
        
        from database.db import get_db
        from database.repositories.users import UserRepository
        from database.repositories.queue import QueueRepository
        from database.repositories.connections import ConnectionsRepository
        
        db = get_db()
        users_repo = UserRepository(db)
        queue_repo = QueueRepository(db)
        connections_repo = ConnectionsRepository(db)
        
        total = await users_repo.count_all()
        in_queue = await queue_repo.count_all()
        connected = await connections_repo.count_active()
        
        await message.reply(
            f"📊 **Statistics**\n\n"
            f"Total users: {total}\n"
            f"In queue: {in_queue}\n"
            f"Connected: {connected}"
        )
    
    @app.on_message(filters.command("reports") & filters.private)
    async def handle_reports_command(client: Client, message: Message):
        """Handle /reports command."""
        telegram_id = message.from_user.id
        
        if not is_admin(telegram_id):
            await message.reply("❌ Access denied.")
            return
        
        from database.db import get_db
        from database.repositories.reports import ReportsRepository
        
        db = get_db()
        reports_repo = ReportsRepository(db)
        
        reports = await reports_repo.get_pending_reports(limit=10)
        
        if not reports:
            await message.reply("✅ No pending reports.")
            return
        
        text = "🚩 **Pending Reports:**\n\n"
        for report in reports:
            text += f"• ID {report['id']}: User {report['reported_id']} - {report['reason']}\n"
        
        await message.reply(text)
    
    @app.on_message(filters.command("addcoins") & filters.private)
    async def handle_addcoins_command(client: Client, message: Message):
        """Handle /addcoins command."""
        telegram_id = message.from_user.id
        
        if not is_admin(telegram_id):
            await message.reply("❌ Access denied.")
            return
        
        if len(message.command) < 3:
            await message.reply("Usage: /addcoins PUBLIC_ID AMOUNT")
            return
        
        public_id = message.command[1]
        try:
            amount = int(message.command[2])
        except ValueError:
            await message.reply("Amount must be a number.")
            return
        
        user = await profile_service.get_user_by_public_id(public_id)
        
        if not user:
            await message.reply(f"❌ User {public_id} not found.")
            return
        
        from database.db import get_db
        from database.repositories.wallet import WalletRepository
        
        db = get_db()
        wallet_repo = WalletRepository(db)
        
        await wallet_repo.add_coins(user["id"], amount)
        await wallet_repo.add_transaction(
            user_id=user["id"],
            amount=amount,
            transaction_type="admin_bonus",
            description=f"Admin bonus by {telegram_id}",
        )
        
        await message.reply(f"✅ Added {amount} coins to {public_id}.")
    
    @app.on_message(filters.private)
    async def handle_admin_input(client: Client, message: Message):
        """Handle admin input for ban/unban."""
        telegram_id = message.from_user.id
        
        if not is_admin(telegram_id):
            return
        
        from bot.states.registration import RegistrationStates
        state = await RegistrationStates.get_state(telegram_id)
        
        if not state:
            return
        
        step = state.get("step")
        
        if step == "banning_user":
            public_id = message.text.strip()
            
            user = await profile_service.get_user_by_public_id(public_id)
            
            if not user:
                await message.reply(f"❌ User {public_id} not found.")
                await RegistrationStates.clear_state(telegram_id)
                return
            
            from database.db import get_db
            from database.repositories.users import UserRepository
            
            db = get_db()
            users_repo = UserRepository(db)
            
            await users_repo.ban_user(user["telegram_user_id"])
            
            await message.reply(f"✅ User {public_id} has been banned.")
            await RegistrationStates.clear_state(telegram_id)
        
        elif step == "unbanning_user":
            public_id = message.text.strip()
            
            user = await profile_service.get_user_by_public_id(public_id)
            
            if not user:
                await message.reply(f"❌ User {public_id} not found.")
                await RegistrationStates.clear_state(telegram_id)
                return
            
            from database.db import get_db
            from database.repositories.users import UserRepository
            
            db = get_db()
            users_repo = UserRepository(db)
            
            await users_repo.unban_user(user["telegram_user_id"])
            
            await message.reply(f"✅ User {public_id} has been unbanned.")
            await RegistrationStates.clear_state(telegram_id)
