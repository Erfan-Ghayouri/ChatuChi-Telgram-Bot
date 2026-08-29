"""
Database connection and initialization.
"""

import aiosqlite
from pathlib import Path


class Database:
    """Async SQLite database connection manager."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection: aiosqlite.Connection | None = None
    
    async def connect(self) -> None:
        """Establish database connection with WAL mode."""
        # Ensure parent directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self._connection = await aiosqlite.connect(self.db_path)
        self._connection.row_factory = aiosqlite.Row
        
        # Enable WAL mode for better concurrency
        await self._connection.execute("PRAGMA journal_mode=WAL")
        await self._connection.execute("PRAGMA synchronous=NORMAL")
        await self._connection.execute("PRAGMA foreign_keys=ON")
        
        await self._connection.commit()
    
    async def close(self) -> None:
        """Close database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
    
    async def execute(
        self, 
        query: str, 
        params: tuple | dict | None = None,
        fetch: bool = False,
        fetch_all: bool = False,
    ):
        """Execute a SQL query."""
        if not self._connection:
            raise RuntimeError("Database not connected")
        
        cursor = await self._connection.execute(query, params or ())
        
        if fetch:
            return await cursor.fetchone()
        elif fetch_all:
            return await cursor.fetchall()
        
        await self._connection.commit()
        return cursor
    
    async def executemany(
        self, 
        query: str, 
        params_list: list[tuple | dict],
    ) -> None:
        """Execute a SQL query with multiple parameter sets."""
        if not self._connection:
            raise RuntimeError("Database not connected")
        
        await self._connection.executemany(query, params_list)
        await self._connection.commit()
    
    @property
    def connection(self) -> aiosqlite.Connection:
        """Get the underlying connection."""
        if not self._connection:
            raise RuntimeError("Database not connected")
        return self._connection
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# Global database instance
db: Database | None = None


def get_db() -> Database:
    """Get the global database instance."""
    if not db:
        raise RuntimeError("Database not initialized")
    return db


async def init_database(db_path: str) -> Database:
    """Initialize the global database instance."""
    global db
    db = Database(db_path)
    await db.connect()
    return db
