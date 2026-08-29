"""
Matchmaking service for connecting users.
"""

import asyncio
from datetime import datetime
from typing import Optional, Tuple

from config import FILTER_MATCH_COST
from database.db import Database
from database.repositories.users import UserRepository
from database.repositories.queue import QueueRepository
from database.repositories.connections import ConnectionRepository
from database.repositories.blocks import BlocksRepository
from database.repositories.wallet import WalletRepository


class MatchmakingService:
    """Service for matchmaking operations."""
    
    def __init__(self, db: Database):
        self.db = db
        self.user_repo = UserRepository(db)
        self.queue_repo = QueueRepository(db)
        self.conn_repo = ConnectionRepository(db)
        self.block_repo = BlocksRepository(db)
        self.wallet_repo = WalletRepository(db)
        
        # Lock for thread-safe matching
        self._match_lock = asyncio.Lock()
    
    async def join_queue(
        self,
        user_id: int,
        telegram_user_id: int,
        mode: str,
        sex_filter: Optional[str] = None,
        city_filter: Optional[str] = None,
    ) -> bool:
        """
        Add user to matchmaking queue.
        
        Returns True if successfully added.
        """
        # Check if already in queue
        if await self.queue_repo.is_in_queue(user_id):
            return False
        
        # Check if already connected
        if await self.conn_repo.is_connected(user_id):
            return False
        
        # Add to queue
        await self.queue_repo.add(
            user_id=user_id,
            mode=mode,
            sex_filter=sex_filter,
            city_filter=city_filter,
        )
        
        # Update user status
        status = "waiting_random" if mode == "random" else "waiting_filtered"
        await self.user_repo.update_status(telegram_user_id, status)
        
        return True
    
    async def leave_queue(self, telegram_user_id: int) -> bool:
        """Remove user from queue. Returns True if was in queue."""
        user = await self.user_repo.get_by_telegram_id(telegram_user_id)
        if not user:
            return False
        
        removed = await self.queue_repo.remove(user["id"])
        if removed:
            await self.user_repo.update_status(telegram_user_id, "idle")
        
        return removed
    
    async def try_match(self) -> Optional[Tuple[dict, dict]]:
        """
        Try to find a match for users in queue.
        
        Returns tuple of (user_a, user_b) if match found, None otherwise.
        """
        async with self._match_lock:
            # Get all waiting users
            waiting = await self.queue_repo.get_all_waiting()
            
            if len(waiting) < 2:
                return None
            
            # Try to match first user with someone compatible
            first = waiting[0]
            exclude_ids = {first["user_id"]}
            
            match = None
            
            if first["mode"] == "random":
                # Look for any random match
                match = await self.queue_repo.find_match_random(exclude_ids)
            else:
                # Filtered match
                match = await self.queue_repo.find_match_filtered(
                    user_sex=first.get("sex"),
                    user_city=first.get("city"),
                    sex_filter=first.get("sex_filter"),
                    city_filter=first.get("city_filter"),
                    exclude_ids=exclude_ids,
                )
            
            if not match:
                return None
            
            # Check for blocks between users
            if await self.block_repo.is_blocked(first["user_id"], match["user_id"]):
                # Remove blocked match and try again
                await self.queue_repo.remove(match["user_id"])
                return None
            
            # Found a match! Create connection
            user_a = await self.user_repo.get_by_id(first["user_id"])
            user_b = await self.user_repo.get_by_id(match["user_id"])
            
            if not user_a or not user_b:
                return None
            
            # Remove both from queue
            await self.queue_repo.remove(first["user_id"])
            await self.queue_repo.remove(match["user_id"])
            
            # Create connection
            conn_id = await self.conn_repo.create(first["user_id"], match["user_id"])
            
            # Update statuses
            await self.user_repo.update_status(user_a["telegram_user_id"], "connected")
            await self.user_repo.update_status(user_b["telegram_user_id"], "connected")
            
            # Charge coin for filtered match (only for the initiator)
            if first["mode"] == "filtered":
                new_balance = await self.user_repo.add_coins(
                    user_a["telegram_user_id"], 
                    -FILTER_MATCH_COST
                )
                await self.wallet_repo.add_transaction(
                    user_id=first["user_id"],
                    amount=-FILTER_MATCH_COST,
                    transaction_type="filtered_match",
                    description=f"Filtered match connection #{conn_id}",
                )
            
            return (user_a, user_b)
    
    async def end_connection(self, telegram_user_id: int) -> bool:
        """End current connection for user. Returns True if ended."""
        user = await self.user_repo.get_by_telegram_id(telegram_user_id)
        if not user:
            return False
        
        ended = await self.conn_repo.end_by_user(user["id"])
        if ended:
            await self.user_repo.update_status(telegram_user_id, "idle")
        
        return ended
    
    async def is_in_queue(self, telegram_user_id: int) -> bool:
        """Check if user is in queue."""
        user = await self.user_repo.get_by_telegram_id(telegram_user_id)
        if not user:
            return False
        return await self.queue_repo.is_in_queue(user["id"])
    
    async def is_connected(self, telegram_user_id: int) -> bool:
        """Check if user is in active connection."""
        user = await self.user_repo.get_by_telegram_id(telegram_user_id)
        if not user:
            return False
        return await self.conn_repo.is_connected(user["id"])
    
    async def get_partner(self, telegram_user_id: int) -> Optional[dict]:
        """Get partner's user info for current connection."""
        user = await self.user_repo.get_by_telegram_id(telegram_user_id)
        if not user:
            return None
        
        conn = await self.conn_repo.get_active_for_user(user["id"])
        if not conn:
            return None
        
        partner_id = await self.conn_repo.get_partner_id(user["id"], conn["id"])
        if not partner_id:
            return None
        
        return await self.user_repo.get_by_id(partner_id)
    
    async def cleanup_stale(self) -> dict:
        """Clean up stale queue entries and connections."""
        queue_cleaned = await self.queue_repo.cleanup_stale()
        conn_cleaned = await self.conn_repo.cleanup_stale()
        
        return {
            "queue_cleaned": queue_cleaned,
            "connections_cleaned": conn_cleaned,
        }
