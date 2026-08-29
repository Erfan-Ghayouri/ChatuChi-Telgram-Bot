"""
ChatuChi Configuration Management

Loads environment variables and provides configuration constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot credentials
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_USERNAME = os.getenv("BOT_USERNAME", "")

# Admin IDs (comma-separated)
ADMIN_IDS = set(
    int(x.strip()) 
    for x in os.getenv("ADMIN_IDS", "").split(",") 
    if x.strip().isdigit()
)

# Database
BASE_DIR = Path(__file__).parent
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "chatuchi.db"))

# Ensure data directory exists
Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)

# Economy settings
INITIAL_COINS = int(os.getenv("INITIAL_COINS", "1"))
FILTER_MATCH_COST = int(os.getenv("FILTER_MATCH_COST", "1"))
REFERRAL_REWARD = int(os.getenv("REFERRAL_REWARD", "1"))

# Rate limiting (seconds between allowed actions)
RATE_LIMIT_MESSAGES = int(os.getenv("RATE_LIMIT_MESSAGES", "5"))
RATE_LIMIT_COMMANDS = int(os.getenv("RATE_LIMIT_COMMANDS", "10"))

# Minimum age requirement
MIN_AGE = 18

# Public ID settings
PUBLIC_ID_PREFIX = "CC-"
PUBLIC_ID_LENGTH = 6  # Characters after prefix (e.g., CC-7F42A9)

# Queue cleanup (seconds)
QUEUE_STALE_TIMEOUT = 3600  # 1 hour
CONNECTION_STALE_TIMEOUT = 7200  # 2 hours

# Validation
def validate_config() -> bool:
    """Validate required configuration."""
    required = ["BOT_TOKEN", "API_ID", "API_HASH", "BOT_USERNAME"]
    for key in required:
        value = globals().get(key)
        if not value or (isinstance(value, int) and value == 0):
            print(f"ERROR: Missing required config: {key}")
            return False
    
    if not ADMIN_IDS:
        print("WARNING: No admin IDs configured")
    
    return True
