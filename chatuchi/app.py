"""
ChatuChi - Anonymous Telegram Chat Bot
Main application entry point
"""
import asyncio
import logging
import os
from pyrogram import Client
import config
from database.db import init_db, cleanup_stale_entries
from bot.handlers.start import register_start_handlers
from bot.handlers.profile import register_profile_handlers
from bot.handlers.matchmaking import register_matchmaking_handlers
from bot.handlers.chat import register_chat_handlers
from bot.handlers.wallet import register_wallet_handlers
from bot.handlers.referral import register_referral_handlers
from bot.handlers.likes import register_likes_handlers
from bot.handlers.moderation import register_moderation_handlers
from bot.handlers.admin import register_admin_handlers
from bot.services.matchmaking import MatchmakingService
from bot.services.relay import RelayService
from bot.services.wallet import WalletService
from bot.services.referral import ReferralService
from bot.services.moderation import ModerationService
from bot.services.profile import ProfileService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def background_cleanup(app: Client):
    """Background task to clean up stale queue entries and connections."""
    while True:
        try:
            await asyncio.sleep(300)  # Run every 5 minutes
            await cleanup_stale_entries()
            logger.info("Completed background cleanup task")
        except Exception as e:
            logger.error(f"Error in background cleanup: {e}")


async def main():
    """Main application entry point."""
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Validate configuration
    config.validate_config()
    
    # Initialize database
    logger.info("Initializing database...")
    await init_db()
    
    # Get database instance for services
    from database.db import get_db
    db_instance = get_db()
    
    # Initialize services
    logger.info("Initializing services...")
    matchmaking_service = MatchmakingService(db_instance)
    relay_service = RelayService(None, db_instance)  # Client will be set later
    wallet_service = WalletService(db_instance)
    referral_service = ReferralService(db_instance)
    moderation_service = ModerationService(db_instance)
    profile_service = ProfileService(db_instance)
    
    # Initialize bot client
    logger.info("Starting ChatuChi bot...")
    app = Client(
        "chatuchi_bot",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN
    )
    
    # Set client for relay service
    relay_service.client = app
    
    # Register handlers
    register_start_handlers(app, profile_service)
    register_profile_handlers(app, profile_service)
    register_matchmaking_handlers(app, matchmaking_service, profile_service)
    register_chat_handlers(app, relay_service, matchmaking_service)
    register_wallet_handlers(app, wallet_service)
    register_referral_handlers(app, referral_service)
    register_likes_handlers(app, profile_service)
    register_moderation_handlers(app, moderation_service)
    register_admin_handlers(app, moderation_service, profile_service)
    
    # Start background cleanup task
    asyncio.create_task(background_cleanup(app))
    
    # Run the bot
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
