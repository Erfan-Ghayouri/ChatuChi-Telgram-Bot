"""
Reports repository.
"""

from typing import Optional

from database.db import Database


class ReportsRepository:
    """Repository for reports-related database operations."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def create_report(
        self,
        reporter_id: int,
        reported_id: int,
        reason: str,
        details: Optional[str] = None,
    ) -> int:
        """Create a new report. Returns report ID."""
        cursor = await self.db.execute(
            """
            INSERT INTO reports (reporter_id, reported_id, reason, details, status)
            VALUES (?, ?, ?, ?, 'pending')
            """,
            (reporter_id, reported_id, reason, details),
        )
        return cursor.lastrowid
    
    async def get_pending_count(self) -> int:
        """Get count of pending reports."""
        row = await self.db.execute(
            "SELECT COUNT(*) as count FROM reports WHERE status = 'pending'",
            fetch=True,
        )
        return row["count"] if row else 0
    
    async def get_pending_reports(self, limit: int = 50) -> list[dict]:
        """Get pending reports."""
        rows = await self.db.execute(
            """
            SELECT r.*, 
                   u1.public_id as reporter_public_id,
                   u2.public_id as reported_public_id
            FROM reports r
            JOIN users u1 ON r.reporter_id = u1.id
            JOIN users u2 ON r.reported_id = u2.id
            WHERE r.status = 'pending'
            ORDER BY r.created_at DESC
            LIMIT ?
            """,
            (limit,),
            fetch_all=True,
        )
        return [dict(row) for row in rows]
    
    async def update_status(self, report_id: int, status: str) -> None:
        """Update report status (pending, reviewed, resolved, dismissed)."""
        await self.db.execute(
            "UPDATE reports SET status = ? WHERE id = ?",
            (status, report_id),
        )
    
    async def get_reports_for_user(self, user_id: int) -> list[dict]:
        """Get all reports for a specific user."""
        rows = await self.db.execute(
            """
            SELECT r.*, u.public_id as reporter_public_id
            FROM reports r
            JOIN users u ON r.reporter_id = u.id
            WHERE r.reported_id = ?
            ORDER BY r.created_at DESC
            """,
            (user_id,),
            fetch_all=True,
        )
        return [dict(row) for row in rows]
    
    async def count_reports_for_user(self, user_id: int) -> int:
        """Count total reports for a user."""
        row = await self.db.execute(
            "SELECT COUNT(*) as count FROM reports WHERE reported_id = ?",
            (user_id,),
            fetch=True,
        )
        return row["count"] if row else 0
    
    async def count_pending_for_user(self, user_id: int) -> int:
        """Count pending reports for a user."""
        row = await self.db.execute(
            "SELECT COUNT(*) as count FROM reports WHERE reported_id = ? AND status = 'pending'",
            (user_id,),
            fetch=True,
        )
        return row["count"] if row else 0
