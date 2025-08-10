import json
import secrets
from typing import Optional, Dict, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import redis
from app.config import settings


class RedisSession:
    """Simple Redis-based session management"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            decode_responses=True
        )
        self.secret = settings.session_secret
        self.expire_seconds = settings.session_expire_seconds
    
    def generate_session_id(self) -> str:
        """Generate a random session ID"""
        return secrets.token_urlsafe(32)
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data from Redis"""
        try:
            data = self.redis_client.get(f"session:{session_id}")
            if data:
                return json.loads(data)
            return None
        except Exception:
            return None
    
    def set_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Set session data in Redis"""
        try:
            self.redis_client.setex(
                f"session:{session_id}",
                self.expire_seconds,
                json.dumps(data)
            )
            return True
        except Exception:
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session from Redis"""
        try:
            self.redis_client.delete(f"session:{session_id}")
            return True
        except Exception:
            return False
    
    def find_session_by_username(self, username: str) -> Optional[tuple[str, Dict[str, Any]]]:
        """Find existing session by username"""
        try:
            # Get all session keys
            session_keys = self.redis_client.keys("session:*")
            for key in session_keys:
                session_id = key.replace("session:", "")
                data = self.get_session(session_id)
                if data and data.get("username") == username:
                    return session_id, data
            return None
        except Exception:
            return None


# Global session instance
session_manager = RedisSession()


def get_session_id(request: Request) -> Optional[str]:
    """Get session ID from request cookies"""
    return request.cookies.get("session_id")


def set_session_id(response: Response, session_id: str) -> None:
    """Set session ID in response cookies"""
    response.set_cookie(
        key="session_id",
        value=session_id,
        max_age=settings.session_expire_seconds,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )


def get_session_data(request: Request) -> Optional[Dict[str, Any]]:
    """Get session data from request"""
    session_id = get_session_id(request)
    if session_id:
        return session_manager.get_session(session_id)
    return None


def set_session_data(request: Request, response: Response, data: Dict[str, Any]) -> str:
    """Set session data and return session ID - reuse existing session if available"""
    # Check if user already has a session
    username = data.get("username")
    if username:
        existing_session = session_manager.find_session_by_username(username)
        if existing_session:
            session_id, existing_data = existing_session
            # Update existing session with new data
            session_manager.set_session(session_id, data)
            set_session_id(response, session_id)
            return session_id
    
    # Create new session if no existing session found
    session_id = get_session_id(request)
    if not session_id:
        session_id = session_manager.generate_session_id()
        set_session_id(response, session_id)
    
    session_manager.set_session(session_id, data)
    return session_id


def clear_session(request: Request, response: Response) -> None:
    """Clear session data"""
    session_id = get_session_id(request)
    if session_id:
        session_manager.delete_session(session_id)
        response.delete_cookie("session_id")
