from telethon import TelegramClient, events, Button
from telethon.tl.types import DocumentAttributeVideo
import os
import time
import logging
from datetime import datetime, timedelta
import asyncio

# Import modules
from config import *
from database import db
from shortener import LinkShortener
from broadcast import BroadcastManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize bot
bot = TelegramClient('terabox_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Initialize managers
shortener = LinkShortener()
broadcast_manager = BroadcastManager(bot)

# Broadcast state storage
broadcast_states = {}

# User cooldown tracking
user_last_request = {}

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in ADMINS

def format_time(seconds: int) -> str:
    """Format seconds to readable time"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"

# ============================================
# USER COMMANDS
# ============================================

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = event.sender_id
    user = await event.get_sender()
    
    # Check if banned
    if db.is_banned(user_id):
        await event.respond("🚫 **You are banned from using this bot.**")
        return
    
    # Add user to database
    user_data = {
        'user_id': user_id,
        'username': user.username or 'No username',
        'first_name': user.first_name or 'No name',
        'last_active': time.time()
    }
    db.add_user(user_id, user_data)
    
    # Check token status
    is_verified = db.is_verified(user_id)
    token_valid = db.is_token_valid(user_id)
    
    message = START_MESSAGE.format(
        duration=TOKEN_DURATION_HOURS,
        validity=TOKEN_VALIDITY_DAYS * 24
    )
    
    if token_valid:
        buttons = [
            [Button.inline("✅ Token Active", b"token_status")],
            [Button.inline("📊 My Stats", b"my_stats"), 
             Button.inline("❓ Help", b"help")]
        ]
    else:
        buttons = [
            [Button.inline("🔐 Generate Token", b"generate_token")],
            [Button.inline("📊 My Stats", b"my_stats"), 
             Button.inline("❓ Help", b"help")]
        ]
    
    await event.respond(message, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=b'generate_token'))
async def generate_token_callback(event):
    user_id = event.sender_id
    
    # Check if already verified
    if db.is_verified(user_id) and db.is_token_valid(user_id):
        await event.answer("✅ Your token is already active!", alert=True)
        return
    
    # Generate verification link
    verify_url = f"{VERIFICATION_URL}?id={user_id}"
    short_url = shortener.shorten(verify_url)
    
    message = VERIFY_MESSAGE.format(
        duration=TOKEN_DURATION_HOURS,
        validity=TOKEN_VALIDITY_DAYS * 24
    )
    
    buttons = [
        [Button.url("🔗 Click Here to Verify", short_url)],
        [Button.inline("✅ I Verified", b"check_verification")],
        [Button.inline("🔙 Back", b"back_to_start")]
    ]
    
    await event.edit(message, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=b'check_verification'))
async def check_verification(event):
    user_id = event.sender_id
    
    # In real implementation, check if user completed shortlink
    # For now, we'll mark as verified (you'll need to implement actual verification)
    
    if db.is_verified(user_id):
        # Generate token
        token_data = {
            'user_id': user_id,
            'generated_at': time.time(),
            'expires_at': time.time() + (TOKEN_DURATION_HOURS * 3600)
        }
        db.save_token(user_id, token_data)
        
        next_verify = datetime.now() + timedelta(days=TOKEN_VALIDITY_DAYS)
        
        message = TOKEN_ACTIVE_MESSAGE.format(
            duration=TOKEN_DURATION_HOURS,
            next_verify=next_verify.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        buttons = [
            [Button.inline("🎬 Send Terabox Link", b"how_to_use")],
            [Button.inline("📊 My Stats", b"my_stats")]
        ]
        
        await event.edit(message, buttons=buttons)
    else:
        await event.answer(
            "❌ Verification not completed! Please complete the verification first.",
            alert=True
        )

@bot.on(events.NewMessage(pattern=r'https?://.*(terabox|1024terabox)\.(com|app)'))
async def handle_terabox_link(event):
    user_id = event.sender_id
    
    # Check if banned
    if db.is_banned(user_id):
        return
    
    # Check token validity
    if not db.is_token_valid(user_id):
        await event.respond(
            "⚠️ **Token Expired or Invalid!**\n\n"
            "Please generate a new token to use the bot.",
            buttons=[[Button.inline("🔐 Generate Token", b"generate_token")]]
        )
        return
    
    # Anti-spam check
    if user_id in user_last_request:
        time_diff = time.time() - user_last_request[user_id]
        if time_diff < 60:
            await event.respond(f"⏳ Wait {int(60 - time_diff)} seconds")
            return
    
    user_last_request[user_id] = time.time()
    
    link = event.message.text
    msg = await event.respond(
        f"🔍 **Processing Terabox link...**\n\n"
        f"Link: `{link[:50]}...`"
    )
    
    # Your terabox processing logic here
    await msg.edit(
        "✅ **Video Found!**\n\n"
        "📹 Video processing will be implemented here\n"
        "🎬 This is the token verification system demo"
    )

# ============================================
# ADMIN COMMANDS - BROADCAST SYSTEM
# ============================================

@bot.on(events.NewMessage(pattern='/broadcast'))
async def broadcast_command(event):
    user_id = event.sender_id
    
    if not is_admin(user_id):
