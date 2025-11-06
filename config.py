import os

# ============================================
# TELEGRAM BOT CONFIGURATION
# ============================================
API_ID = int(os.getenv('API_ID', '123456'))
API_HASH = os.getenv('API_HASH', 'your_api_hash')
BOT_TOKEN = os.getenv('BOT_TOKEN', 'your_bot_token')

# ============================================
# ADMIN CONFIGURATION
# ============================================
ADMINS = [1234567890, 9876543210]  # Admin user IDs
BOT_USERNAME = os.getenv('BOT_USERNAME', 'your_bot_username')

# ============================================
# REDIS DATABASE CONFIGURATION
# ============================================
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

# ============================================
# LINK SHORTENER API CONFIGURATION
# ============================================
# Supported: gplinks, droplink, earn4link, shrinkme, bitly, cutt.ly, etc.

SHORTENER_API = os.getenv('SHORTENER_API', '')  # Your shortener API key
SHORTENER_DOMAIN = os.getenv('SHORTENER_DOMAIN', 'gplinks.co')  # Domain name
SHORTENER_TYPE = os.getenv('SHORTENER_TYPE', 'gplinks')  # gplinks, droplink, earn4link, shrinkme, bitly

# Example configurations for different shorteners:
# GPLinks: API from gplinks.co/member/tools/api
# Droplink: API from droplink.co/member/tools/api
# Earn4Link: API from earn4link.in/member/tools/api
# ShrinkMe: API from shrinkme.io/member/tools/api
# Bitly: API from bitly.com/a/your_access_token

# ============================================
# TOKEN SYSTEM CONFIGURATION
# ============================================
TOKEN_DURATION_HOURS = int(os.getenv('TOKEN_DURATION_HOURS', '1'))  # Default: 1 hour
TOKEN_VALIDITY_DAYS = int(os.getenv('TOKEN_VALIDITY_DAYS', '1'))  # Default: 24 hours (1 day)
VERIFICATION_URL = os.getenv('VERIFICATION_URL', 'https://your-website.com/verify')  # Verification page

# ============================================
# FORCE SUBSCRIBE CONFIGURATION
# ============================================
FORCE_CHANNEL = os.getenv('FORCE_CHANNEL', '@YourChannel')  # Force subscribe channel
FORCE_CHANNEL_ID = int(os.getenv('FORCE_CHANNEL_ID', '-1001234567890'))

# ============================================
# STORAGE CONFIGURATION
# ============================================
PRIVATE_CHAT_ID = int(os.getenv('PRIVATE_CHAT_ID', '-1001234567890'))  # Storage channel
DOWNLOAD_FOLDER = 'downloads'

# ============================================
# TERABOX CONFIGURATION
# ============================================
TERABOX_COOKIE = os.getenv('TERABOX_COOKIE', '')
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '2000'))  # MB
DOWNLOAD_TIMEOUT = int(os.getenv('DOWNLOAD_TIMEOUT', '3600'))  # seconds

# ============================================
# BOT MESSAGES CONFIGURATION
# ============================================
START_MESSAGE = """
👋 **Welcome to Terabox Video Player Bot!**

🎬 **Features:**
✅ Direct video playback in Telegram
✅ Fast downloads from Terabox
✅ Token-based access system
✅ Anti-spam protection

📝 **How to use:**
1. Click button below to generate token
2. Complete verification (once per {validity} hours)
3. Send Terabox link
4. Enjoy your video!

💡 **Token valid for:** {duration} hour(s)
⏰ **Verification needed:** Once per {validity} hours
"""

VERIFY_MESSAGE = """
🔐 **Token Verification Required!**

Your token has expired or you need to verify.

⏰ **Token Duration:** {duration} hour(s)
🔄 **Re-verification:** Every {validity} hours

**Steps:**
1. Click the button below
2. Complete the verification
3. Come back and click "✅ I Verified"

⚠️ **Note:** Verification supports our bot development!
"""

TOKEN_ACTIVE_MESSAGE = """
✅ **Token Activated Successfully!**

🎉 Your token is now active!
⏰ Valid for: {duration} hour(s)
🔄 Next verification: {next_verify}

🎬 **Now you can:**
• Send Terabox links
• Download videos
• Watch directly in Telegram

💡 Send a Terabox link to start!
"""

# ============================================
# ADMIN PANEL MESSAGES
# ============================================
ADMIN_PANEL = """
⚙️ **Admin Control Panel**

**Current Settings:**
• Token Duration: {duration} hour(s)
• Validity Period: {validity} hours
• Shortener: {shortener}
• Total Users: {users}
• Active Tokens: {active}

**Commands:**
/setduration <hours> - Set token duration
/setvalidity <hours> - Set validity period
/stats - Bot statistics
/broadcast - Send message to all users
/ban <user_id> - Ban user
/unban <user_id> - Unban user
"""
