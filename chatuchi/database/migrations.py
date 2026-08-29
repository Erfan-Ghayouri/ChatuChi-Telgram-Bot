"""
Database schema migrations.
"""

from database.db import Database


MIGRATIONS = [
    # Migration 1: Initial schema - users table
    "CREATE TABLE IF NOT EXISTS users (\n        id INTEGER PRIMARY KEY AUTOINCREMENT,\n        telegram_user_id INTEGER UNIQUE NOT NULL,\n        public_id TEXT UNIQUE NOT NULL,\n        name TEXT NOT NULL,\n        city TEXT,\n        age INTEGER NOT NULL,\n        sex TEXT NOT NULL,\n        bio TEXT DEFAULT '',\n        coins INTEGER DEFAULT 0,\n        likes_received INTEGER DEFAULT 0,\n        likes_given INTEGER DEFAULT 0,\n        status TEXT DEFAULT 'offline',\n        is_banned INTEGER DEFAULT 0,\n        is_verified_age INTEGER DEFAULT 0,\n        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n        referrer_id INTEGER,\n        FOREIGN KEY (referrer_id) REFERENCES users(id)\n    );",
    "CREATE INDEX IF NOT EXISTS idx_users_telegram ON users(telegram_user_id);",
    "CREATE INDEX IF NOT EXISTS idx_users_public_id ON users(public_id);",
    "CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);",
    "CREATE INDEX IF NOT EXISTS idx_users_city ON users(city);",
    
    # Migration 2: Queue table
    "CREATE TABLE IF NOT EXISTS queue (\n        id INTEGER PRIMARY KEY AUTOINCREMENT,\n        user_id INTEGER UNIQUE NOT NULL,\n        mode TEXT NOT NULL,\n        sex_filter TEXT,\n        city_filter TEXT,\n        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE\n    );",
    "CREATE INDEX IF NOT EXISTS idx_queue_user_id ON queue(user_id);",
    
    # Migration 3: Connections table
    "CREATE TABLE IF NOT EXISTS connections (\n        id INTEGER PRIMARY KEY AUTOINCREMENT,\n        user_a INTEGER NOT NULL,\n        user_b INTEGER NOT NULL,\n        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n        ended_at TIMESTAMP,\n        active INTEGER DEFAULT 1,\n        FOREIGN KEY (user_a) REFERENCES users(id) ON DELETE CASCADE,\n        FOREIGN KEY (user_b) REFERENCES users(id) ON DELETE CASCADE\n    );",
    "CREATE INDEX IF NOT EXISTS idx_connections_active ON connections(active);",
    "CREATE INDEX IF NOT EXISTS idx_connections_user_a ON connections(user_a);",
    "CREATE INDEX IF NOT EXISTS idx_connections_user_b ON connections(user_b);",
    
    # Migration 4: Likes table
    "CREATE TABLE IF NOT EXISTS likes (\n        id INTEGER PRIMARY KEY AUTOINCREMENT,\n        from_user INTEGER NOT NULL,\n        to_user INTEGER NOT NULL,\n        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n        FOREIGN KEY (from_user) REFERENCES users(id) ON DELETE CASCADE,\n        FOREIGN KEY (to_user) REFERENCES users(id) ON DELETE CASCADE,\n        UNIQUE(from_user, to_user)\n    );",
    "CREATE INDEX IF NOT EXISTS idx_likes_from_user ON likes(from_user);",
    "CREATE INDEX IF NOT EXISTS idx_likes_to_user ON likes(to_user);",
    
    # Migration 5: Blocks table
    "CREATE TABLE IF NOT EXISTS blocks (\n        id INTEGER PRIMARY KEY AUTOINCREMENT,\n        blocker_id INTEGER NOT NULL,\n        blocked_id INTEGER NOT NULL,\n        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n        FOREIGN KEY (blocker_id) REFERENCES users(id) ON DELETE CASCADE,\n        FOREIGN KEY (blocked_id) REFERENCES users(id) ON DELETE CASCADE,\n        UNIQUE(blocker_id, blocked_id)\n    );",
    "CREATE INDEX IF NOT EXISTS idx_blocks_blocker ON blocks(blocker_id);",
    "CREATE INDEX IF NOT EXISTS idx_blocks_blocked ON blocks(blocked_id);",
    
    # Migration 6: Reports table
    "CREATE TABLE IF NOT EXISTS reports (\n        id INTEGER PRIMARY KEY AUTOINCREMENT,\n        reporter_id INTEGER NOT NULL,\n        reported_id INTEGER NOT NULL,\n        reason TEXT NOT NULL,\n        details TEXT,\n        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n        status TEXT DEFAULT 'pending',\n        FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE CASCADE,\n        FOREIGN KEY (reported_id) REFERENCES users(id) ON DELETE CASCADE\n    );",
    "CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);",
    "CREATE INDEX IF NOT EXISTS idx_reports_reported ON reports(reported_id);",
    
    # Migration 7: Referrals table
    "CREATE TABLE IF NOT EXISTS referrals (\n        id INTEGER PRIMARY KEY AUTOINCREMENT,\n        inviter_id INTEGER NOT NULL,\n        referred_id INTEGER NOT NULL,\n        rewarded INTEGER DEFAULT 0,\n        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n        FOREIGN KEY (inviter_id) REFERENCES users(id) ON DELETE CASCADE,\n        FOREIGN KEY (referred_id) REFERENCES users(id) ON DELETE CASCADE,\n        UNIQUE(inviter_id, referred_id)\n    );",
    "CREATE INDEX IF NOT EXISTS idx_referrals_inviter ON referrals(inviter_id);",
    "CREATE INDEX IF NOT EXISTS idx_referrals_referred ON referrals(referred_id);",
    "CREATE INDEX IF NOT EXISTS idx_referrals_rewarded ON referrals(rewarded);",
    
    # Migration 8: Wallet transactions table
    "CREATE TABLE IF NOT EXISTS wallet_transactions (\n        id INTEGER PRIMARY KEY AUTOINCREMENT,\n        user_id INTEGER NOT NULL,\n        amount INTEGER NOT NULL,\n        transaction_type TEXT NOT NULL,\n        description TEXT,\n        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE\n    );",
    "CREATE INDEX IF NOT EXISTS idx_wallet_user_id ON wallet_transactions(user_id);",
    "CREATE INDEX IF NOT EXISTS idx_wallet_created_at ON wallet_transactions(created_at);",
    
    # Migration 9: Settings table
    "CREATE TABLE IF NOT EXISTS settings (\n        key TEXT PRIMARY KEY,\n        value TEXT,\n        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n    );",
    
    # Migration 10: Registration states table
    "CREATE TABLE IF NOT EXISTS registration_states (\n        telegram_id INTEGER PRIMARY KEY,\n        state_data TEXT,\n        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n    );",
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
    
    # Add trigger for updating timestamp (separate statement)
    try:
        await db.execute("""
            CREATE TRIGGER IF NOT EXISTS update_users_updated_at 
            AFTER UPDATE ON users 
            BEGIN
                UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
        """)
        print("Trigger created successfully")
    except Exception as e:
        print(f"Trigger creation failed: {e}")
    
    print("All migrations completed successfully")


async def get_migration_count(db: Database) -> int:
    """Get the number of applied migrations (based on table existence)."""
    # Check if the last migration table exists
    result = await db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='settings'",
        fetch=True,
    )
    return len(MIGRATIONS) if result else 0
