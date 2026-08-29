"""
Database schema migrations.
"""

from database.db import Database


MIGRATIONS = [
    # Migration 1: Initial schema
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_user_id INTEGER UNIQUE NOT NULL,
        public_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        city TEXT,
        age INTEGER NOT NULL,
        sex TEXT NOT NULL,
        bio TEXT DEFAULT '',
        coins INTEGER DEFAULT 0,
        likes_received INTEGER DEFAULT 0,
        likes_given INTEGER DEFAULT 0,
        status TEXT DEFAULT 'offline',
        is_banned INTEGER DEFAULT 0,
        is_verified_age INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        referrer_id INTEGER,
        FOREIGN KEY (referrer_id) REFERENCES users(id)
    );
    
    CREATE INDEX IF NOT EXISTS idx_users_telegram ON users(telegram_user_id);
    CREATE INDEX IF NOT EXISTS idx_users_public_id ON users(public_id);
    CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);
    CREATE INDEX IF NOT EXISTS idx_users_city ON users(city);
    """,
    
    # Migration 2: Queue table
    """
    CREATE TABLE IF NOT EXISTS queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        mode TEXT NOT NULL,
        sex_filter TEXT,
        city_filter TEXT,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    
    CREATE INDEX IF NOT EXISTS idx_queue_user_id ON queue(user_id);
    """,
    
    # Migration 3: Connections table
    """
    CREATE TABLE IF NOT EXISTS connections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_a INTEGER NOT NULL,
        user_b INTEGER NOT NULL,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ended_at TIMESTAMP,
        active INTEGER DEFAULT 1,
        FOREIGN KEY (user_a) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (user_b) REFERENCES users(id) ON DELETE CASCADE
    );
    
    CREATE INDEX IF NOT EXISTS idx_connections_active ON connections(active);
    CREATE INDEX IF NOT EXISTS idx_connections_user_a ON connections(user_a);
    CREATE INDEX IF NOT EXISTS idx_connections_user_b ON connections(user_b);
    """,
    
    # Migration 4: Likes table
    """
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user INTEGER NOT NULL,
        to_user INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (from_user) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (to_user) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE(from_user, to_user)
    );
    
    CREATE INDEX IF NOT EXISTS idx_likes_from_user ON likes(from_user);
    CREATE INDEX IF NOT EXISTS idx_likes_to_user ON likes(to_user);
    """,
    
    # Migration 5: Blocks table
    """
    CREATE TABLE IF NOT EXISTS blocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        blocker_id INTEGER NOT NULL,
        blocked_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (blocker_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (blocked_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE(blocker_id, blocked_id)
    );
    
    CREATE INDEX IF NOT EXISTS idx_blocks_blocker ON blocks(blocker_id);
    CREATE INDEX IF NOT EXISTS idx_blocks_blocked ON blocks(blocked_id);
    """,
    
    # Migration 6: Reports table
    """
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reporter_id INTEGER NOT NULL,
        reported_id INTEGER NOT NULL,
        reason TEXT NOT NULL,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (reported_id) REFERENCES users(id) ON DELETE CASCADE
    );
    
    CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);
    CREATE INDEX IF NOT EXISTS idx_reports_reported ON reports(reported_id);
    """,
    
    # Migration 7: Referrals table
    """
    CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inviter_id INTEGER NOT NULL,
        referred_id INTEGER NOT NULL,
        rewarded INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (inviter_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (referred_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE(inviter_id, referred_id)
    );
    
    CREATE INDEX IF NOT EXISTS idx_referrals_inviter ON referrals(inviter_id);
    CREATE INDEX IF NOT EXISTS idx_referrals_referred ON referrals(referred_id);
    CREATE INDEX IF NOT EXISTS idx_referrals_rewarded ON referrals(rewarded);
    """,
    
    # Migration 8: Wallet transactions table
    """
    CREATE TABLE IF NOT EXISTS wallet_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        transaction_type TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    
    CREATE INDEX IF NOT EXISTS idx_wallet_user_id ON wallet_transactions(user_id);
    CREATE INDEX IF NOT EXISTS idx_wallet_created_at ON wallet_transactions(created_at);
    """,
    
    # Migration 9: Settings table
    """
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
]


async def run_migrations(db: Database) -> None:
    """Run all database migrations."""
    for i, migration in enumerate(MIGRATIONS, start=1):
        try:
            await db.execute(migration)
            print(f"Migration {i} completed successfully")
        except Exception as e:
            print(f"Migration {i} failed: {e}")
            raise
    
    # Update timestamp on users table
    await db.execute("""
        CREATE TRIGGER IF NOT EXISTS update_users_updated_at 
        AFTER UPDATE ON users 
        BEGIN
            UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
    """)
    
    print("All migrations completed successfully")


async def get_migration_count(db: Database) -> int:
    """Get the number of applied migrations (based on table existence)."""
    # Check if the last migration table exists
    result = await db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='settings'",
        fetch=True,
    )
    return len(MIGRATIONS) if result else 0
