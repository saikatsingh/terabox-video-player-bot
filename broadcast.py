import asyncio
import logging
from typing import List, Dict
from telethon import TelegramClient
from telethon.errors import (
    UserIsBlockedError, 
    InputUserDeactivatedError,
    UserIdInvalidError,
    PeerIdInvalidError,
    FloodWaitError
)
from database import db

logger = logging.getLogger(__name__)

class BroadcastManager:
    def __init__(self, bot: TelegramClient):
        self.bot = bot
        self.active_broadcasts = {}
    
    async def send_broadcast(
        self, 
        admin_id: int,
        message_text: str = None,
        message_file: str = None,
        reply_markup = None,
        pin_message: bool = False,
        disable_notification: bool = False
    ) -> Dict:
        """
        Send broadcast message to all users
        
        Args:
            admin_id: Admin who initiated broadcast
            message_text: Text message to send
            message_file: File path/URL to send
            reply_markup: Buttons to attach
            pin_message: Whether to pin the message
            disable_notification: Silent notification
        
        Returns:
            Dictionary with broadcast statistics
        """
        users = db.get_all_users()
        
        stats = {
            'total': len(users),
            'success': 0,
            'failed': 0,
            'blocked': 0,
            'deleted': 0,
            'errors': []
        }
        
        # Store broadcast ID
        broadcast_id = f"{admin_id}_{int(asyncio.get_event_loop().time())}"
        self.active_broadcasts[broadcast_id] = {
            'status': 'running',
            'stats': stats
        }
        
        logger.info(f"📢 Broadcast started by Admin {admin_id}")
        logger.info(f"📊 Total users: {stats['total']}")
        
        for index, user_id in enumerate(users, 1):
            try:
                # Skip banned users
                if db.is_banned(user_id):
                    stats['failed'] += 1
                    continue
                
                # Send message
                if message_file:
                    # Send media message
                    await self.bot.send_file(
                        user_id,
                        message_file,
                        caption=message_text,
                        buttons=reply_markup,
                        silent=disable_notification
                    )
                else:
                    # Send text message
                    sent_msg = await self.bot.send_message(
                        user_id,
                        message_text,
                        buttons=reply_markup,
                        link_preview=False,
                        silent=disable_notification
                    )
                    
                    # Pin message if requested
                    if pin_message:
                        try:
                            await self.bot.pin_message(user_id, sent_msg.id, notify=False)
                        except:
                            pass
                
                stats['success'] += 1
                
                # Progress update every 50 users
                if index % 50 == 0:
                    await self._send_progress(admin_id, stats, index, len(users))
                
                # Anti-flood delay
                await asyncio.sleep(0.1)
                
            except UserIsBlockedError:
                stats['blocked'] += 1
                stats['failed'] += 1
                logger.warning(f"⚠️ User {user_id} blocked the bot")
                
            except InputUserDeactivatedError:
                stats['deleted'] += 1
                stats['failed'] += 1
                logger.warning(f"⚠️ User {user_id} deleted account")
                
            except (UserIdInvalidError, PeerIdInvalidError):
                stats['failed'] += 1
                logger.warning(f"⚠️ Invalid user ID: {user_id}")
                
            except FloodWaitError as e:
                wait_time = e.seconds
                logger.warning(f"⚠️ FloodWait: Sleeping for {wait_time} seconds")
                await asyncio.sleep(wait_time)
                # Retry this user
                try:
                    if message_file:
                        await self.bot.send_file(
                            user_id, message_file, 
                            caption=message_text, 
                            buttons=reply_markup
                        )
                    else:
                        await self.bot.send_message(
                            user_id, message_text, 
                            buttons=reply_markup
                        )
                    stats['success'] += 1
                except:
                    stats['failed'] += 1
                    
            except Exception as e:
                stats['failed'] += 1
                error_msg = f"User {user_id}: {str(e)}"
                stats['errors'].append(error_msg)
                logger.error(f"❌ Broadcast error: {error_msg}")
        
        # Mark broadcast as completed
        self.active_broadcasts[broadcast_id]['status'] = 'completed'
        
        logger.info(f"✅ Broadcast completed!")
        logger.info(f"📊 Success: {stats['success']}, Failed: {stats['failed']}")
        
        return stats
    
    async def _send_progress(self, admin_id: int, stats: Dict, current: int, total: int):
        """Send progress update to admin"""
        try:
            progress = (current / total) * 100
            message = (
                f"📢 **Broadcast Progress**\n\n"
                f"📊 Progress: {progress:.1f}% ({current}/{total})\n\n"
                f"✅ Success: {stats['success']}\n"
                f"❌ Failed: {stats['failed']}\n"
                f"🚫 Blocked: {stats['blocked']}\n"
                f"👻 Deleted: {stats['deleted']}"
            )
            await self.bot.send_message(admin_id, message)
        except Exception as e:
            logger.error(f"Failed to send progress: {e}")
    
    async def broadcast_to_specific_users(
        self,
        user_ids: List[int],
        message_text: str,
        message_file: str = None,
        reply_markup = None
    ) -> Dict:
        """
        Broadcast to specific users only
        """
        stats = {
            'total': len(user_ids),
            'success': 0,
            'failed': 0
        }
        
        for user_id in user_ids:
            try:
                if message_file:
                    await self.bot.send_file(
                        user_id, message_file, 
                        caption=message_text, 
                        buttons=reply_markup
                    )
                else:
                    await self.bot.send_message(
                        user_id, message_text, 
                        buttons=reply_markup
                    )
                stats['success'] += 1
                await asyncio.sleep(0.1)
            except:
                stats['failed'] += 1
        
        return stats
    
    async def broadcast_to_active_users(
        self,
        admin_id: int,
        message_text: str,
        message_file: str = None,
        reply_markup = None
    ) -> Dict:
        """
        Broadcast only to users with active tokens
        """
        all_users = db.get_all_users()
        active_users = [uid for uid in all_users if db.is_token_valid(uid)]
        
        logger.info(f"📢 Broadcasting to {len(active_users)} active users")
        
        return await self.broadcast_to_specific_users(
            active_users,
            message_text,
            message_file,
            reply_markup
        )
    
    def get_broadcast_status(self, broadcast_id: str) -> Dict:
        """Get status of ongoing broadcast"""
        return self.active_broadcasts.get(broadcast_id, {})

# Global broadcast manager instance (initialized in main.py)
broadcast_manager = None
