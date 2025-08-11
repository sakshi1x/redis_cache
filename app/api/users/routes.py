import json
import time
from typing import Optional, Dict, Any, List
import redis
from app.core.config import settings
from app.services.caching.redis_client import RedisHashClient
from app.utils.helpers import convert_numeric_fields


class RedisUserProfiles:
    """Redis Hash-based user profile management using base client"""
    
    def __init__(self):
        self.redis_client = RedisHashClient()
        self.numeric_fields = ["questions_asked", "login_count", "last_login", "created_at"]

    # ---- Key helpers ----
    def _profile_key(self, employee_id: str) -> str:
        return self.redis_client.build_key_parts("user", employee_id, "profile")

    def _legacy_profile_key(self, employee_id: str) -> str:
        # Old structure we want to deprecate: ...:profile:data
        return self.redis_client.build_key_parts("user", employee_id, "profile", "data")

    def _migrate_legacy_profile_if_needed(self, employee_id: str) -> None:
        """If only the legacy key exists, migrate to canonical key and delete legacy.
        This keeps Redis tidy and prevents duplicate folders in the browser.
        """
        canonical_key = self._profile_key(employee_id)
        legacy_key = self._legacy_profile_key(employee_id)
        if not self.redis_client.key_exists(legacy_key):
            return
        if self.redis_client.key_exists(canonical_key):
            # Canonical already present; just remove the legacy key
            self.redis_client.delete_key(legacy_key)
            return
        # Move data from legacy -> canonical, then delete legacy
        data = self.redis_client.hget_all(legacy_key) or {}
        if data:
            self.redis_client.hset_mapping(
                canonical_key,
                data,
                settings.USER_PROFILE_EXPIRE_SECONDS,
            )
        self.redis_client.delete_key(legacy_key)
    
    def create_user_profile(self, employee_id: str, username: str, password: str, 
                          department: str = None, role: str = None) -> bool:
        """Create a new user profile with extended data"""
        current_time = self.redis_client._get_current_timestamp()
        user_key = self._profile_key(employee_id)
        
        # Set default values if not provided
        department = department or settings.DEFAULT_DEPARTMENT
        role = role or settings.DEFAULT_ROLE
        
        # Set initial profile data
        profile_data = {
            "employee_id": employee_id,
            "username": username,
            "password": password,
            "department": department,
            "role": role,
            "questions_asked": "0",
            "login_count": "0",
            "last_login": str(current_time),
            "created_at": str(current_time),
            "status": settings.DEFAULT_USER_STATUS
        }
        
        ok = self.redis_client.hset_mapping(
            user_key,
            profile_data,
            settings.USER_PROFILE_EXPIRE_SECONDS,
        )
        # Clean up any leftover legacy key to avoid duplicates in folders
        self.redis_client.delete_key(self._legacy_profile_key(employee_id))
        return bool(ok)
    
    def get_user_profile(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Get complete user profile"""
        # Ensure legacy data is migrated away first
        self._migrate_legacy_profile_if_needed(employee_id)
        user_key = self._profile_key(employee_id)
        profile = self.redis_client.hget_all(user_key)
        
        if not profile:
            return None
        
        return convert_numeric_fields(profile, self.numeric_fields)
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Find user profile by username"""
        user_keys = self.redis_client.get_keys_by_pattern(
            self.redis_client.build_pattern_parts("user", "*", "profile")
        )
        
        for key in user_keys:
            # Check if the key is a hash (user profile)
            key_type = self.redis_client.get_key_type(key)
            if key_type != "hash":
                continue
            
            profile = self.redis_client.hget_all(key)
            if profile and profile.get("username") == username:
                return convert_numeric_fields(profile, self.numeric_fields)
        
        return None
    
    def update_login_activity(self, employee_id: str) -> bool:
        """Update user's login activity"""
        self._migrate_legacy_profile_if_needed(employee_id)
        user_key = self._profile_key(employee_id)
        current_time = self.redis_client._get_current_timestamp()
        
        try:
            pipeline = self.redis_client.redis_client.pipeline()
            pipeline.hincrby(user_key, "login_count", 1)
            pipeline.hset(user_key, "last_login", current_time)
            pipeline.execute()
            return True
        except Exception as e:
            print(f"Error updating login activity: {e}")
            return False
    
    def increment_questions_asked(self, employee_id: str) -> bool:
        """Increment user's questions asked counter"""
        self._migrate_legacy_profile_if_needed(employee_id)
        user_key = self._profile_key(employee_id)
        inc = self.redis_client.hincr_by(user_key, "questions_asked", 1)
        return inc is not None
    
    def update_user_field(self, employee_id: str, field: str, value: str) -> bool:
        """Update a specific field in user profile"""
        self._migrate_legacy_profile_if_needed(employee_id)
        user_key = self._profile_key(employee_id)
        ok = self.redis_client.hset_field(user_key, field, value)
        return bool(ok)
    
    def get_user_stats(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Get user statistics"""
        self._migrate_legacy_profile_if_needed(employee_id)
        user_key = self._profile_key(employee_id)
        stats = self.redis_client.hget_fields(user_key, self.numeric_fields)
        
        if not stats[0]:  # No user found
            return None
        
        return {
            "questions_asked": int(stats[0]) if stats[0] else 0,
            "login_count": int(stats[1]) if stats[1] else 0,
            "last_login": int(stats[2]) if stats[2] else 0,
            "created_at": int(stats[3]) if stats[3] else 0
        }
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all user profiles (for admin purposes)"""
        user_keys = self.redis_client.get_keys_by_pattern(
            self.redis_client.build_pattern_parts("user", "*", "profile")
        )
        users = []
        
        for key in user_keys:
            # Check if the key is a hash (user profile)
            key_type = self.redis_client.get_key_type(key)
            if key_type != "hash":
                continue
            
            profile = self.redis_client.hget_all(key)
            if profile:
                users.append(convert_numeric_fields(profile, self.numeric_fields))
        
        return users
    
    def delete_user_profile(self, employee_id: str) -> bool:
        """Delete user profile"""
        user_key = self._profile_key(employee_id)
        ok_main = self.redis_client.delete_key(user_key)
        # Best-effort cleanup of any legacy key left over
        self.redis_client.delete_key(self._legacy_profile_key(employee_id))
        return bool(ok_main)
    
    def user_exists(self, employee_id: str) -> bool:
        """Check if user profile exists"""
        self._migrate_legacy_profile_if_needed(employee_id)
        user_key = self._profile_key(employee_id)
        return self.redis_client.key_exists(user_key)
    
    def username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        return self.get_user_by_username(username) is not None

    def cleanup_all_legacy_profiles(self) -> int:
        """Migrate and remove any legacy profile keys left in Redis.
        Returns the number of legacy keys processed.
        """
        legacy_keys = self.redis_client.get_keys_by_pattern(
            self.redis_client.build_pattern_parts("user", "*", "profile", "data")
        )
        processed = 0
        for key in legacy_keys:
            parts = key.split(":")
            try:
                user_index = parts.index("user") + 1
                employee_id = parts[user_index]
            except Exception:
                continue
            self._migrate_legacy_profile_if_needed(employee_id)
            processed += 1
        return processed


# Global user profiles instance
user_profiles = RedisUserProfiles()
