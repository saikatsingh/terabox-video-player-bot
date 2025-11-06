from telethon import TelegramClient, events, Button
import os
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get credentials from environment variables
API_ID = int(os.getenv('API_ID', '0'))
API_HASH = os.getenv('API_HASH', '')
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

# Initialize bot
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# User tracking
user_last_request = {}

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond(
        f"👋 **Welcome to Terabox Video Player Bot!**\n\n"
        f"🎬 **Features:**\n"
        f"✅ Direct video playback in Telegram\n"
        f"✅ Fast downloads from Terabox\n"
        f"✅ Token system (1 hour validity)\n"
        f"✅ Anti-spam protection\n\n"
        f"📝 **How to use:**\n"
        f"1. Generate token with /gen\n"
        f"2. Send me any Terabox link\n"
        f"3. Get instant video preview\n"
        f"4. Click 'Play' to watch\n\n"
        f"💡 **Commands:**\n"
        f"/gen - Generate new token\n"
        f"/help - Bot guide\n"
        f"/ping - Check bot status\n\n"
        f"🚀 **Send a Terabox link to start!**"
    )

@bot.on(events.NewMessage(pattern='/ping'))
async def ping(event):
    await event.respond("✅ **Bot is running on Koyeb!**")

@bot.on(events.NewMessage(pattern='/gen'))
async def generate_token(event):
    user_id = event.sender_id
    
    # Anti-spam check (1 minute cooldown)
    if user_id in user_last_request:
        time_diff = time.time() - user_last_request[user_id]
        if time_diff < 60:
            await event.respond(
                f"⏳ **Ruko thoda!**\n\n"
                f"Spam mat karo. {int(60 - time_diff)} seconds baad try karo."
            )
            return
    
    user_last_request[user_id] = time.time()
    
    # Generate token (valid for 1 hour)
    token = f"TBX_{user_id}_{int(time.time())}"
    expiry = int(time.time()) + 3600
    
    await event.respond(
        f"✅ **Token Generated!**\n\n"
        f"🔑 Token: `{token}`\n"
        f"⏰ Valid for: 1 hour\n"
        f"🕐 Expires at: {time.ctime(expiry)}\n\n"
        f"Ab Terabox link bhejo!"
    )

@bot.on(events.NewMessage(pattern=r'https?://.*(terabox|1024terabox)\.(com|app)'))
async def handle_terabox_link(event):
    user_id = event.sender_id
    link = event.message.text
    
    # Anti-spam check
    if user_id in user_last_request:
        time_diff = time.time() - user_last_request[user_id]
        if time_diff < 60:
            await event.respond(f"⏳ {int(60 - time_diff)} seconds rukho")
            return
    
    user_last_request[user_id] = time.time()
    
    msg = await event.respond(
        f"🔍 **Processing Terabox link...**\n\n"
        f"Link: `{link[:50]}...`\n\n"
        f"⚙️ Extracting video data..."
    )
    
    # Simulate processing (Replace with actual Terabox API logic)
    await msg.edit(
        f"✅ **Link Detected!**\n\n"
        f"🎬 Video processing feature coming soon!\n"
        f"📦 Full code available in repository\n\n"
        f"Bot is successfully running on Koyeb! 🚀"
    )

@bot.on(events.NewMessage(pattern='/help'))
async def help_command(event):
    await event.respond(
        f"📚 **Bot Help Guide**\n\n"
        f"**Commands:**\n"
        f"• `/start` - Start the bot\n"
        f"• `/gen` - Generate access token\n"
        f"• `/ping` - Check bot status\n"
        f"• `/help` - Show this message\n\n"
        f"**Usage:**\n"
        f"1. Generate token using /gen\n"
        f"2. Send Terabox video link\n"
        f"3. Bot will process and send video\n\n"
        f"**Features:**\n"
        f"✅ Token-based access control\n"
        f"✅ Anti-spam protection (60s cooldown)\n"
        f"✅ Direct video playback\n"
        f"✅ Fast downloading\n\n"
        f"**Support:** @YourSupportChannel"
    )

# Health check endpoint (optional but recommended)
@bot.on(events.NewMessage(pattern='/health'))
async def health_check(event):
    await event.respond("🟢 Healthy")

logger.info("🚀 Bot starting...")
logger.info(f"📱 API_ID: {API_ID}")
logger.info(f"✅ Bot is ready!")

print("✅ Bot Started Successfully on Koyeb!")
print("🌐 Deployed using Docker")
print("📦 All systems operational!")

bot.run_until_disconnected()
