import json
import time
from typing import Optional, Dict, Any
import redis
from app.config import settings


class RedisUserProfiles:
    """Redis Hash-based user profile management"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            decode_responses=True
        )
    
    def create_user_profile(self, employee_id: str, username: str, password: str, 
                          department: str = "General", role: str = "Employee") -> bool:
        """Create a new user profile with extended data"""
        try:
            current_time = int(time.time())
            user_key = f"user:{employee_id}"
            
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
                "status": "active"
            }
            
            # Use pipeline for atomic operation
            pipeline = self.redis_client.pipeline()
            pipeline.hset(user_key, mapping=profile_data)
            pipeline.expire(user_key, 86400 * 365)  # Expire after 1 year
            pipeline.execute()
            
            return True
        except Exception as e:
            print(f"Error creating user profile: {e}")
            return False
    
    def get_user_profile(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Get complete user profile"""
        try:
            user_key = f"user:{employee_id}"
            profile = self.redis_client.hgetall(user_key)
            
            if not profile:
                return None
            
            # Convert numeric strings back to integers where appropriate
            if profile.get("questions_asked"):
                profile["questions_asked"] = int(profile["questions_asked"])
            if profile.get("login_count"):
                profile["login_count"] = int(profile["login_count"])
            if profile.get("last_login"):
                profile["last_login"] = int(profile["last_login"])
            if profile.get("created_at"):
                profile["created_at"] = int(profile["created_at"])
            
            return profile
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Find user profile by username"""
        try:
            # Get all user keys
            user_keys = self.redis_client.keys("user:*")
            
            for key in user_keys:
                profile = self.redis_client.hgetall(key)
                if profile.get("username") == username:
                    # Convert numeric strings back to integers
                    if profile.get("questions_asked"):
                        profile["questions_asked"] = int(profile["questions_asked"])
                    if profile.get("login_count"):
                        profile["login_count"] = int(profile["login_count"])
                    if profile.get("last_login"):
                        profile["last_login"] = int(profile["last_login"])
                    if profile.get("created_at"):
                        profile["created_at"] = int(profile["created_at"])
                    
                    return profile
            
            return None
        except Exception as e:
            print(f"Error finding user by username: {e}")
            return None
    
    def update_login_activity(self, employee_id: str) -> bool:
        """Update user's login activity"""
        try:
            user_key = f"user:{employee_id}"
            current_time = int(time.time())
            
            pipeline = self.redis_client.pipeline()
            pipeline.hincrby(user_key, "login_count", 1)
            pipeline.hset(user_key, "last_login", current_time)
            pipeline.execute()
            
            return True
        except Exception as e:
            print(f"Error updating login activity: {e}")
            return False
    
    def increment_questions_asked(self, employee_id: str) -> bool:
        """Increment user's questions asked counter"""
        try:
            user_key = f"user:{employee_id}"
            self.redis_client.hincrby(user_key, "questions_asked", 1)
            return True
        except Exception as e:
            print(f"Error incrementing questions asked: {e}")
            return False
    
    def update_user_field(self, employee_id: str, field: str, value: str) -> bool:
        """Update a specific field in user profile"""
        try:
            user_key = f"user:{employee_id}"
            self.redis_client.hset(user_key, field, value)
            return True
        except Exception as e:
            print(f"Error updating user field: {e}")
            return False
    
    def get_user_stats(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Get user statistics"""
        try:
            user_key = f"user:{employee_id}"
            stats = self.redis_client.hmget(user_key, "questions_asked", "login_count", "last_login", "created_at")
            
            if not stats[0]:  # No user found
                return None
            
            return {
                "questions_asked": int(stats[0]) if stats[0] else 0,
                "login_count": int(stats[1]) if stats[1] else 0,
                "last_login": int(stats[2]) if stats[2] else 0,
                "created_at": int(stats[3]) if stats[3] else 0
            }
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return None
    
    def get_all_users(self) -> list:
        """Get all user profiles (for admin purposes)"""
        try:
            user_keys = self.redis_client.keys("user:*")
            users = []
            
            for key in user_keys:
                profile = self.redis_client.hgetall(key)
                if profile:
                    # Convert numeric strings back to integers
                    if profile.get("questions_asked"):
                        profile["questions_asked"] = int(profile["questions_asked"])
                    if profile.get("login_count"):
                        profile["login_count"] = int(profile["login_count"])
                    if profile.get("last_login"):
                        profile["last_login"] = int(profile["last_login"])
                    if profile.get("created_at"):
                        profile["created_at"] = int(profile["created_at"])
                    
                    users.append(profile)
            
            return users
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def delete_user_profile(self, employee_id: str) -> bool:
        """Delete user profile"""
        try:
            user_key = f"user:{employee_id}"
            self.redis_client.delete(user_key)
            return True
        except Exception as e:
            print(f"Error deleting user profile: {e}")
            return False


# Global user profiles instance
user_profiles = RedisUserProfiles()
