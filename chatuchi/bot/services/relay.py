"""
Message relay service for anonymous chat.

This service copies messages between connected users without exposing
their Telegram identities.
"""

import logging
from typing import Optional

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ParseMode, MessageType

from database.db import Database
from database.repositories.users import UserRepository


logger = logging.getLogger(__name__)


class RelayService:
    """Service for relaying messages between connected users."""
    
    def __init__(self, client: Client, db: Database):
        self.client = client
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def relay_message(
        self,
        source_user_id: int,
        message: Message,
    ) -> bool:
        """
        Relay a message from source user to their connected partner.
        
        Returns True if successfully relayed.
        """
        # Get source user
        source_user = await self.user_repo.get_by_telegram_id(source_user_id)
        if not source_user:
            return False
        
        # Get connection
        from database.repositories.connections import ConnectionRepository
        conn_repo = ConnectionRepository(self.db)
        
        conn = await conn_repo.get_active_for_user(source_user["id"])
        if not conn:
            return False
        
        # Get partner ID
        partner_db_id = await conn_repo.get_partner_id(source_user["id"], conn["id"])
        if not partner_db_id:
            return False
        
        partner = await self.user_repo.get_by_id(partner_db_id)
        if not partner:
            return False
        
        telegram_partner_id = partner["telegram_user_id"]
        
        try:
            # Copy message based on type
            if message.text:
                await self._copy_text(telegram_partner_id, message)
            elif message.photo:
                await self._copy_photo(telegram_partner_id, message)
            elif message.video:
                await self._copy_video(telegram_partner_id, message)
            elif message.voice:
                await self._copy_voice(telegram_partner_id, message)
            elif message.audio:
                await self._copy_audio(telegram_partner_id, message)
            elif message.document:
                await self._copy_document(telegram_partner_id, message)
            elif message.sticker:
                await self._copy_sticker(telegram_partner_id, message)
            elif message.animation:
                await self._copy_animation(telegram_partner_id, message)
            else:
                # Unknown message type - send as text notification
                await self._send_system_message(
                    telegram_partner_id,
                    "📨 Received an unsupported message type",
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error relaying message: {e}")
            
            # Check if partner blocked the bot
            if "BOT_BLOCKED" in str(e) or "PEER_ID_INVALID" in str(e):
                await self._handle_bot_blocked(source_user_id, telegram_partner_id)
            
            return False
    
    async def _copy_text(self, chat_id: int, message: Message) -> None:
        """Copy text message."""
        await self.client.send_message(
            chat_id=chat_id,
            text=message.text,
            parse_mode=ParseMode.MARKDOWN,
        )
    
    async def _copy_photo(self, chat_id: int, message: Message) -> None:
        """Copy photo message."""
        photo = message.photo.file_id
        caption = message.caption or ""
        
        await self.client.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
        )
    
    async def _copy_video(self, chat_id: int, message: Message) -> None:
        """Copy video message."""
        video = message.video.file_id
        caption = message.caption or ""
        
        await self.client.send_video(
            chat_id=chat_id,
            video=video,
            caption=caption,
        )
    
    async def _copy_voice(self, chat_id: int, message: Message) -> None:
        """Copy voice message."""
        voice = message.voice.file_id
        
        await self.client.send_voice(
            chat_id=chat_id,
            voice=voice,
        )
    
    async def _copy_audio(self, chat_id: int, message: Message) -> None:
        """Copy audio message."""
        audio = message.audio.file_id
        caption = message.caption or ""
        
        await self.client.send_audio(
            chat_id=chat_id,
            audio=audio,
            caption=caption,
        )
    
    async def _copy_document(self, chat_id: int, message: Message) -> None:
        """Copy document message."""
        document = message.document.file_id
        caption = message.caption or ""
        
        await self.client.send_document(
            chat_id=chat_id,
            document=document,
            caption=caption,
        )
    
    async def _copy_sticker(self, chat_id: int, message: Message) -> None:
        """Copy sticker message."""
        sticker = message.sticker.file_id
        
        await self.client.send_sticker(
            chat_id=chat_id,
            sticker=sticker,
        )
    
    async def _copy_animation(self, chat_id: int, message: Message) -> None:
        """Copy animation (GIF) message."""
        animation = message.animation.file_id
        caption = message.caption or ""
        
        await self.client.send_animation(
            chat_id=chat_id,
            animation=animation,
            caption=caption,
        )
    
    async def _send_system_message(self, chat_id: int, text: str) -> None:
        """Send a system message."""
        await self.client.send_message(
            chat_id=chat_id,
            text=text,
        )
    
    async def _handle_bot_blocked(
        self, 
        source_user_id: int, 
        partner_telegram_id: int,
    ) -> None:
        """Handle case where partner has blocked the bot."""
        # End the connection
        source_user = await self.user_repo.get_by_telegram_id(source_user_id)
        if not source_user:
            return
        
        from database.repositories.connections import ConnectionRepository
        conn_repo = ConnectionRepository(self.db)
        
        await conn_repo.end_by_user(source_user["id"])
        
        # Update statuses
        await self.user_repo.update_status(source_user_id, "idle")
        
        partner = await self.user_repo.get_by_telegram_id(partner_telegram_id)
        if partner:
            await self.user_repo.update_status(partner_telegram_id, "idle")
        
        # Notify source user
        await self._send_system_message(
            source_user_id,
            "⚠️ Your partner has blocked the bot. Connection ended.",
        )
