# ChatuChi - Anonymous Chat Bot

## Overview

**ChatuChi** is a production-ready Telegram anonymous chat bot that connects users randomly while keeping their identities private. Built with Python 3.11+ and Kurigram (actively maintained Pyrogram fork).

## Features

- 🔒 **Complete Anonymity**: Never exposes Telegram username, ID, or profile to chat partners
- 🎯 **Matchmaking**: Random free matching and filtered matching (by sex/city)
- 👤 **Anonymous Profiles**: Unique public IDs (e.g., `CC-7F42A9`) separate from Telegram identity
- 💰 **Wallet System**: Coins for filtered matches, earned through referrals
- ❤️ **Likes System**: Rate-limited likes between users after chats
- 🚫 **Block/Report**: Safety features with admin moderation panel
- 🏙️ **Iran Cities**: Comprehensive province/city selection with pagination
- 🔗 **Referral System**: Earn coins by inviting friends
- ⚡ **Async Architecture**: Built with asyncio for high concurrency
- 🛡️ **Privacy-First**: Minimal data storage, no message logging

## Project Structure

```
chatuchi/
├── app.py                  # Main entry point
├── config.py               # Configuration management
├── requirements.txt        # Dependencies
├── .env.example            # Environment template
├── README.md               # This file
│
├── bot/
│   ├── handlers/           # Telegram command/callback handlers
│   │   ├── start.py
│   │   ├── profile.py
│   │   ├── matchmaking.py
│   │   ├── chat.py
│   │   ├── wallet.py
│   │   ├── referral.py
│   │   ├── likes.py
│   │   ├── moderation.py
│   │   └── admin.py
│   │
│   ├── keyboards/          # Keyboard builders
│   │   ├── main.py
│   │   ├── profile.py
│   │   ├── matching.py
│   │   └── chat.py
│   │
│   ├── states/             # FSM states for registration
│   │   └── registration.py
│   │
│   ├── services/           # Business logic
│   │   ├── matchmaking.py
│   │   ├── relay.py
│   │   ├── wallet.py
│   │   ├── referral.py
│   │   ├── moderation.py
│   │   └── profile.py
│   │
│   ├── utils/              # Utilities
│   │   ├── ids.py
│   │   ├── pagination.py
│   │   └── helpers.py
│   │
│   └── texts.py            # User-facing strings
│
├── database/
│   ├── db.py               # Database connection & initialization
│   ├── migrations.py       # Schema migrations
│   └── repositories/       # Data access layer
│       ├── users.py
│       ├── queue.py
│       ├── connections.py
│       ├── likes.py
│       ├── reports.py
│       ├── blocks.py
│       ├── referrals.py
│       └── wallet.py
│
├── data/
│   └── iran_cities.json    # Iran provinces and cities
│
└── tests/
    ├── test_matchmaking.py
    ├── test_wallet.py
    ├── test_referrals.py
    └── test_profiles.py
```

## Installation

### Prerequisites

- Python 3.11 or higher
- Telegram Bot Token (from @BotFather)
- Telegram API ID and Hash (from my.telegram.org)

### Step 1: Clone/Setup

```bash
cd chatuchi
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
BOT_TOKEN=your_bot_token_from_botfather
API_ID=your_api_id_from_my_telegram_org
API_HASH=your_api_hash_from_my_telegram_org
BOT_USERNAME=your_bot_username_without_at
ADMIN_IDS=comma_separated_telegram_user_ids_of_admins
DATABASE_PATH=data/chatuchi.db
INITIAL_COINS=1
FILTER_MATCH_COST=1
REFERRAL_REWARD=1
```

### Step 4: Get Bot Credentials

1. **Bot Token**: Message @BotFather on Telegram:
   - Send `/newbot`
   - Follow instructions to create bot
   - Copy the token

2. **API ID/Hash**: Visit https://my.telegram.org/apps
   - Log in with your Telegram account
   - Create a new application
   - Copy API ID and API Hash

3. **Admin IDs**: Get your Telegram user ID from @userinfobot
   - Add it to ADMIN_IDS (comma-separated for multiple admins)

### Step 5: Initialize Database

The database initializes automatically on first run. Migrations are applied automatically.

### Step 6: Run the Bot

```bash
python app.py
```

## Bot Commands

### User Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and main menu |
| `/profile` | View your profile |
| `/editprofile` | Edit your profile |
| `/find` | Start matchmaking with filters |
| `/random` | Random free matchmaking |
| `/filters` | Set matchmaking filters |
| `/stop` | End current chat |
| `/wallet` | View coin balance and transactions |
| `/invite` | Get referral link |
| `/likes` | View likes received/given |
| `/report` | Report a user |
| `/block` | Block a user |
| `/help` | Help and safety information |
| `/settings` | Bot settings |

### Admin Commands

| Command | Description |
|---------|-------------|
| `/admin` | Admin panel |
| `/ban` | Ban a user (by public ID) |
| `/unban` | Unban a user |
| `/reports` | View pending reports |
| `/user` | Inspect user details |
| `/stats` | Bot statistics |
| `/addcoins` | Add coins to user |
| `/removecoins` | Remove coins from user |

## Database Schema

### Tables

- **users**: User profiles (telegram_user_id, public_id, name, city, age, sex, bio, coins, etc.)
- **queue**: Matchmaking queue entries
- **connections**: Active/past chat connections
- **likes**: Like relationships between users
- **blocks**: Blocked user pairs
- **reports**: User reports with reasons
- **referrals**: Referral relationships
- **wallet_transactions**: Coin transaction history

### Indexes

Optimized indexes on frequently queried fields:
- telegram_user_id
- public_id
- queue user_id
- city
- status
- connection users

## Key Features Explained

### Privacy Protection

- Messages are **copied**, not forwarded, to prevent identity leakage
- Telegram usernames, IDs, and profile info are never shown to chat partners
- Only the anonymous profile (name, age, sex, city, bio, public ID) is visible
- No permanent message storage

### Matchmaking Logic

1. **Random Match** (Free): Matches with any available compatible user
2. **Filtered Match** (1 coin): Matches based on sex and/or city filters
   - Coin is charged **only after successful connection**
   - Joining queue does NOT consume coins
   - Failed match does NOT consume coins

### Coin System

- **Initial Balance**: 1 coin (configurable)
- **Earn Coins**: 
  - Referral rewards (+1 per successful referral)
  - Admin bonuses
- **Spend Coins**:
  - Filtered matchmaking (-1 per successful connection)

### Referral System

Each user gets a unique referral link:
```
https://t.me/YOUR_BOT_USERNAME?start=ref_CC7F42A9
```

Rules:
- +1 coin per successful referral
- One reward per referred user (no duplicate rewards)
- No self-referrals allowed

### Safety Features

- **Age Verification**: 18+ only during registration
- **Block**: Prevent future matches with blocked users
- **Report**: Submit reports with categories (spam, harassment, etc.)
- **Rate Limiting**: Anti-spam protection on commands and messages
- **Admin Panel**: Review reports, ban users, manage coins

## Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

Tests cover:
- Profile creation and unique ID generation
- Registration state machine
- Queue operations
- Random and filtered matching
- Blocking and reporting
- Likes system
- Referral rewards
- Wallet transactions
- Race condition prevention

## Production Deployment

### Recommendations

1. **Use PostgreSQL** instead of SQLite for production:
   ```python
   # Update config.py DATABASE_PATH to PostgreSQL connection string
   ```

2. **Enable WAL mode** for SQLite (enabled by default in this project)

3. **Set up logging** to a file or service like Sentry

4. **Use environment variables** for all secrets

5. **Run with a process manager** like systemd or supervisor:
   ```ini
   [Unit]
   Description=ChatuChi Bot
   After=network.target

   [Service]
   Type=simple
   User=chatuchi
   WorkingDirectory=/path/to/chatuchi
   ExecStart=/path/to/venv/bin/python app.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

6. **Backup database regularly**:
   ```bash
   cp data/chatuchi.db data/chatuchi.backup.$(date +%Y%m%d).db
   ```

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue on the repository.

---

**Remember**: Never share sensitive personal information (passwords, addresses, financial details) in anonymous chats. Stay safe! 🛡️
