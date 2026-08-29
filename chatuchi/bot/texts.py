"""
ChatuChi - User-facing text strings

Centralized location for all bot messages to support future localization.
"""

# Welcome and Start
WELCOME_TITLE = "✨ Welcome to ChatuChi ✨"
WELCOME_TEXT = """
👋 Anonymous conversations start here!

Meet someone new while keeping your identity completely private.

🛡️ **Safety First:**
• This service is 18+ only
• Never share passwords, addresses, or financial information
• Your Telegram identity is never revealed

Ready to create your anonymous profile?
"""

WELCOME_BUTTONS = {
    "create_profile": "🎯 Create Profile",
    "help": "❓ Help & Safety",
}

# Registration Flow
REGISTRATION_STEPS = {
    "name": {
        "question": "What should we call you?",
        "hint": "Enter a display name (can be fictional):",
    },
    "age": {
        "question": "How old are you?",
        "hint": "You must be 18+ to use ChatuChi:",
    },
    "sex": {
        "question": "What is your sex?",
    },
    "city": {
        "question": "Where are you from?",
    },
    "bio": {
        "question": "Tell us about yourself",
        "hint": "A short bio (optional, press Skip to skip):",
    },
}

SEX_OPTIONS = {
    "male": "👨 Male",
    "female": "👩 Female",
    "other": "🌐 Other",
}

SKIP_BUTTON = "⏭️ Skip"
BACK_BUTTON = "🔙 Back"
CANCEL_BUTTON = "❌ Cancel"

# Profile
PROFILE_VIEW = """
👤 **Anonymous Profile**

**Name:** {name}
**Age:** {age}
**Sex:** {sex}
**City:** {city}

**Bio:**
{bio}

❤️ **Likes:** {likes}
🆔 **ID:** {public_id}
"""

MY_PROFILE_VIEW = """
👤 **Your Profile**

**Name:** {name}
**Age:** {age}
**Sex:** {sex}
**City:** {city}

**Bio:**
{bio}

❤️ **Likes Received:** {likes_received}
❤️ **Likes Given:** {likes_given}
💰 **Coins:** {coins}
🆔 **ID:** {public_id}
"""

PROFILE_EDIT_MENU = """
✏️ **Edit Profile**

What would you like to change?
"""

EDIT_OPTIONS = {
    "name": "✏️ Change Name",
    "age": "🎂 Change Age",
    "sex": "🔄 Change Sex",
    "city": "🏙️ Change City",
    "bio": "📝 Change Bio",
    "back": "🔙 Back to Menu",
}

# Main Menu
MAIN_MENU_TEXT = """
🎯 **What would you like to do?**

Choose an option below:
"""

MAIN_MENU_BUTTONS = {
    "find": "🎯 Find Someone",
    "random": "⚡ Random Match",
    "filters": "🔎 Filters",
    "profile": "👤 My Profile",
    "wallet": "💰 Wallet",
    "likes": "❤️ Likes",
    "invite": "🔗 Invite Friends",
    "settings": "⚙️ Settings",
    "help": "🛡️ Safety / Help",
}

# Matchmaking
FINDING_TEXT = """
🔎 **Finding someone...**

Your filters:
**Sex:** {sex_filter}
**City:** {city_filter}

⏳ Waiting for another person...
"""

MATCH_FOUND_TEXT = """
✨ **Match found!**

You are now connected anonymously.

Start chatting now! 💬
"""

MATCH_FILTERS = {
    "any_sex": "Anyone",
    "any_city": "Any City",
}

FILTER_MENU_TEXT = """
🔎 **Find Someone with Filters**

Set your preferences:
"""

FILTER_OPTIONS = {
    "sex_anyone": "Sex: Anyone",
    "sex_male": "Sex: Male",
    "sex_female": "Sex: Female",
    "city_any": "City: Any",
    "city_select": "Select City",
    "start_filtered": "🚀 Start Filtered Match (1 coin)",
    "back": "🔙 Back",
}

FILTER_COST_WARNING = """
⚠️ **Filtered matching costs 1 coin**

The coin is charged ONLY after a successful connection.
Joining the queue does NOT cost anything.

Current balance: {coins} coins
"""

INSUFFICIENT_COINS = """
❌ **Insufficient coins!**

Filtered matching requires at least 1 coin.

💡 Ways to earn coins:
• Invite friends using /invite
• Wait for admin bonuses

Current balance: {coins} coins
"""

RANDOM_MATCH_START = """
⚡ **Starting random match...**

Looking for anyone available...

This is FREE! 🎉
"""

# Connected Chat
CONNECTED_CHAT_INFO = """
💬 **Connected Anonymously**

You can now chat!

Remember:
• Be respectful
• Don't share personal info
• Use 🚫 Block if needed
"""

CHAT_ENDED_TEXT = """
👋 **Chat ended**

Thanks for chatting!

Would you like to:
"""

PARTNER_LEFT_TEXT = """
🚪 **Your partner left the chat**

The connection has ended.

Would you like to:
"""

CONNECTED_KEYBOARD_BUTTONS = {
    "end_chat": "❌ End Chat",
    "block": "🚫 Block",
    "report": "🚩 Report",
    "like": "❤️ Like",
    "profile": "👤 View Profile",
}

END_CHAT_OPTIONS = {
    "like": "❤️ Like this person",
    "block": "🚫 Block this person",
    "find_again": "🎯 Find Someone New",
    "menu": "🏠 Main Menu",
}

# Wallet
WALLET_VIEW = """
💰 **Your Wallet**

**Balance:** {balance} coins

**Recent Transactions:**
{transactions}

---
💡 **How to earn coins:**
• Invite friends: +{referral_reward} per friend
• Admin bonuses

**How to spend coins:**
• Filtered matchmaking: -{filter_cost} per connection
"""

NO_TRANSACTIONS = "No transactions yet."

TRANSACTION_TYPES = {
    "referral": "🔗 Referral Reward",
    "filtered_match": "🔎 Filtered Match",
    "admin_bonus": "⭐ Admin Bonus",
    "admin_penalty": "⚠️ Admin Penalty",
    "initial": "🎁 Initial Balance",
    "correction": "🔧 Correction",
}

# Referral
REFERRAL_INFO = """
🔗 **Invite Friends & Earn Coins!**

Your referral link:
`{link}`

**Stats:**
• Total invitations: {total}
• Successful referrals: {successful}
• Coins earned: {earned}

Each friend who joins gives you +{reward} coin!
"""

COPY_LINK_BUTTON = "📋 Copy Link"

# Likes
LIKES_INFO = """
❤️ **Your Likes**

**Received:** {received}
**Given:** {given}

People who liked you appreciate the connection!
"""

LIKE_SENT_TEXT = "❤️ You liked this person!"
LIKE_RECEIVED_TEXT = "❤️ Someone liked you after your chat!"

# Reporting
REPORT_MENU = """
🚩 **Report User**

Why are you reporting this user?
"""

REPORT_REASONS = {
    "spam": "📢 Spam",
    "harassment": "😠 Harassment",
    "inappropriate": "🔞 Inappropriate Content",
    "scam": "💰 Scam",
    "other": "📝 Other",
}

REPORT_SUBMITTED = """
✅ **Report submitted**

Thank you for helping keep ChatuChi safe.
Our team will review this report.
"""

# Blocking
BLOCK_CONFIRM = """
🚫 **Block User**

Are you sure you want to block this user?

You will never be matched with them again.
"""

BLOCKED_SUCCESS = "🚫 User blocked successfully."
UNBLOCKED_SUCCESS = "🚫 User unblocked."

# Help & Safety
HELP_TEXT = """
🛡️ **Safety & Help**

**Stay Safe:**
• Never share passwords or financial info
• Don't share your address or phone number
• Be cautious about meeting in person
• Report suspicious behavior

**Commands:**
• /start - Main menu
• /profile - View your profile
• /find - Find someone with filters
• /random - Random free match
• /wallet - View coins
• /invite - Get referral link
• /report - Report a user
• /block - Block a user
• /help - This help message

**Need help?** Contact an admin.
"""

SETTINGS_TEXT = """
⚙️ **Settings**

Manage your preferences:
"""

SETTINGS_OPTIONS = {
    "notifications": "🔔 Notifications",
    "privacy": "🔒 Privacy",
    "language": "🌐 Language",
    "back": "🔙 Back to Menu",
}

# Admin
ADMIN_PANEL = """
👨‍💼 **Admin Panel**

**Statistics:**
• Total users: {total_users}
• Online: {online}
• In queue: {in_queue}
• Connected: {connected}
• Banned: {banned}

**Pending reports:** {pending_reports}
"""

ADMIN_OPTIONS = {
    "stats": "📊 Statistics",
    "reports": "🚩 Reports",
    "users": "👥 Users",
    "ban": "🚫 Ban User",
    "unban": "✅ Unban User",
    "coins": "💰 Manage Coins",
}

USER_ADMIN_VIEW = """
👤 **User Details**

**Public ID:** {public_id}
**Telegram ID:** {telegram_id}
**Name:** {name}
**Age:** {age}
**Sex:** {sex}
**City:** {city}
**Coins:** {coins}
**Status:** {status}
**Banned:** {is_banned}
**Reports:** {report_count}

**Registered:** {created_at}
**Last seen:** {last_seen}
"""

BAN_CONFIRM = """
🚫 **Ban User**

Enter the public ID to ban:
(e.g., CC-7F42A9)
"""

UNBAN_CONFIRM = """
✅ **Unban User**

Enter the public ID to unban:
"""

COIN_MANAGE = """
💰 **Manage Coins**

Enter: public_id amount
(e.g., CC-7F42A9 10)

Use negative amounts to remove coins.
"""

# Errors and Messages
ERROR_NOT_REGISTERED = "❌ Please create a profile first using /start"
ERROR_ALREADY_CONNECTED = "❌ You're already in a chat. Use /stop to end it."
ERROR_NOT_IN_QUEUE = "❌ You're not in the matchmaking queue."
ERROR_NO_ACTIVE_CHAT = "❌ No active chat to end."
ERROR_INVALID_AGE = "❌ You must be 18+ to use ChatuChi."
ERROR_INVALID_INPUT = "❌ Invalid input. Please try again."
ERROR_USER_NOT_FOUND = "❌ User not found."
ERROR_ALREADY_IN_QUEUE = "❌ You're already in the matchmaking queue."
ERROR_RATE_LIMITED = "⏳ Please wait a moment before trying again."
ERROR_BOT_BLOCKED = "⚠️ The other user blocked the bot."
ERROR_CONNECTION_LOST = "⚠️ Connection lost. The other user may have left."

# Status indicators
STATUS_LABELS = {
    "offline": "⚫ Offline",
    "idle": "🟢 Online",
    "filling_profile": "📝 Creating Profile",
    "waiting_random": "🔎 Waiting (Random)",
    "waiting_filtered": "🔎 Waiting (Filtered)",
    "connected": "💬 Connected",
}
