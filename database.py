import redis
import json
import time
from typing import Optional, Dict, List
from config import *

class Database:
    def __init__(self):
        try:
            self.db = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD if REDIS_PASSWORD else None,
                decode_responses=True
            )
            self.db.ping()
            print("✅ Redis connected successfully!")
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            print("⚠️ Using in-memory storage (data will be lost on restart)")
            self.db = None
            self.memory_store = {}
    
    def _get_key(self, prefix: str, user_id: int) -> str:
        return f"{prefix}:{user_id}"
    
    # ============================================
    # USER TOKEN MANAGEMENT
    # ============================================
    
    def save_token(self, user_id: int, token_data: dict):
        """Save user token with expiry"""
        key = self._get_key("token", user_id)
        if self.db:
            self.db.setex(
                key,
                TOKEN_VALIDITY_DAYS * 86400,  # Convert days to seconds
                json.dumps(token_data)
            )
        else:
            self.memory_store[key] = {
                'data': token_data,
                'expiry': time.time() + (TOKEN_VALIDITY_DAYS * 86400)
            }
    
    def get_token(self, user_id: int) -> Optional[dict]:
        """Get user token data"""
        key = self._get_key("token", user_id)
        if self.db:
            data = self.db.get(key)
            return json.loads(data) if data else None
        else:
            stored = self.memory_store.get(key)
            if stored and stored['expiry'] > time.time():
                return stored['data']
            return None
    
    def is_token_valid(self, user_id: int) -> bool:
        """Check if user has valid token"""
        token_data = self.get_token(user_id)
        if not token_data:
            return False
        
        # Check if token is expired
        current_time = time.time()
        token_time = token_data.get('generated_at', 0)
        duration_seconds = TOKEN_DURATION_HOURS * 3600
        
        return (current_time - token_time) < duration_seconds
    
    def delete_token(self, user_id: int):
        """Delete user token"""
        key = self._get_key("token", user_id)
        if self.db:
            self.db.delete(key)
        else:
            self.memory_store.pop(key, None)
    
    # ============================================
    # VERIFICATION TRACKING
    # ============================================
    
    def save_verification(self, user_id: int):
        """Save verification timestamp"""
        key = self._get_key("verify", user_id)
        verify_data = {
            'verified_at': time.time(),
            'expires_at': time.time() + (TOKEN_VALIDITY_DAYS * 86400)
        }
        if self.db:
            self.db.setex(
                key,
                TOKEN_VALIDITY_DAYS * 86400,
                json.dumps(verify_data)
            )
        else:
            self.memory_store[key] = {
                'data': verify_data,
                'expiry': verify_data['expires_at']
            }
    
    def is_verified(self, user_id: int) -> bool:
        """Check if user has completed verification"""
        key = self._get_key("verify", user_id)
        if self.db:
            data = self.db.get(key)
            if data:
                verify_data = json.loads(data)
                return verify_data['expires_at'] > time.time()
        else:
            stored = self.memory_store.get(key)
            if stored and stored['expiry'] > time.time():
                return True
        return False
    
    def get_verification_time(self, user_id: int) -> Optional[float]:
        """Get when user needs to verify again"""
        key = self._get_key("verify", user_id)
        if self.db:
            data = self.db.get(key)
            if data:
                verify_data = json.loads(data)
                return verify_data['expires_at']
        else:
            stored = self.memory_store.get(key)
            if stored:
                return stored['expiry']
        return None
    
    # ============================================
    # USER MANAGEMENT
    # ============================================
    
    def add_user(self, user_id: int, user_data: dict):
        """Add new user to database"""
        key = self._get_key("user", user_id)
        user_data['joined_at'] = time.time()
        if self.db:
            self.db.set(key, json.dumps(user_data))
        else:
            self.memory_store[key] = {'data': user_data, 'expiry': float('inf')}
    
    def get_user(self, user_id: int) -> Optional[dict]:
        """Get user data"""
        key = self._get_key("user", user_id)
        if self.db:
            data = self.db.get(key)
            return json.loads(data) if data else None
        else:
            stored = self.memory_store.get(key)
            return stored['data'] if stored else None
    
    def get_all_users(self) -> List[int]:
        """Get all user IDs"""
        if self.db:
            keys = self.db.keys("user:*")
            return [int(key.split(':')[1]) for key in keys]
        else:
            return [int(key.split(':')[1]) for key in self.memory_store.keys() if key.startswith('user:')]
    
    def ban_user(self, user_id: int):
        """Ban a user"""
        key = self._get_key("ban", user_id)
        if self.db:
            self.db.set(key, "banned")
        else:
            self.memory_store[key] = {'data': 'banned', 'expiry': float('inf')}
    
    def unban_user(self, user_id: int):
        """Unban a user"""
        key = self._get_key("ban", user_id)
        if self.db:
            self.db.delete(key)
        else:
            self.memory_store.pop(key, None)
    
    def is_banned(self, user_id: int) -> bool:
        """Check if user is banned"""
        key = self._get_key("ban", user_id)
        if self.db:
            return self.db.exists(key) > 0
        else:
            return key in self.memory_store
    
    # ============================================
    # STATISTICS
    # ============================================
    
    def get_stats(self) -> dict:
        """Get bot statistics"""
        total_users = len(self.get_all_users())
        
        # Count active tokens
        active_tokens = 0
        for user_id in self.get_all_users():
            if self.is_token_valid(user_id):
                active_tokens += 1
        
        return {
            'total_users': total_users,
            'active_tokens': active_tokens,
            'token_duration': TOKEN_DURATION_HOURS,
            'validity_period': TOKEN_VALIDITY_DAYS * 24  # Convert to hours
        }
    
    # ============================================
    # SETTINGS MANAGEMENT
    # ============================================
    
    def set_token_duration(self, hours: int):
        """Set token duration (admin only)"""
        global TOKEN_DURATION_HOURS
        TOKEN_DURATION_HOURS = hours
        if self.db:
            self.db.set("setting:token_duration", hours)
        else:
            self.memory_store["setting:token_duration"] = {'data': hours, 'expiry': float('inf')}
    
    def set_validity_period(self, hours: int):
        """Set validity period (admin only)"""
        global TOKEN_VALIDITY_DAYS
        TOKEN_VALIDITY_DAYS = hours / 24  # Convert hours to days
        if self.db:
            self.db.set("setting:validity_period", hours)
        else:
            self.memory_store["setting:validity_period"] = {'data': hours, 'expiry': float('inf')}

# Initialize database
db = Database()
