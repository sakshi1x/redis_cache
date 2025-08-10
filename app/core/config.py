from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    app_name: str = "Employee API with Redis Sessions"
    app_version: str = "1.0.0"
    app_description: str = "Simple Employee API with Redis session management"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Logging Configuration
    log_level: str = "INFO"
    
    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # Session Configuration
    session_secret: str = "cool cool"
    session_expire_seconds: int = 3600  # 1 hour
    
    # Redis Key Patterns
    USER_PROFILE_KEY_PATTERN: str = "user:{employee_id}"
    SESSION_KEY_PATTERN: str = "session:{session_id}"
    USER_QUESTIONS_STREAM_PATTERN: str = "user:{employee_id}:questions"
    USER_ANALYTICS_KEY_PATTERN: str = "user:{employee_id}:analytics"
    GLOBAL_ANALYTICS_KEY: str = "global:question_analytics"
    CATEGORY_ANALYTICS_PATTERN: str = "category:{category}:questions"
    
    # Default Values
    DEFAULT_DEPARTMENT: str = "General"
    DEFAULT_ROLE: str = "Employee"
    DEFAULT_CATEGORY: str = "general"
    DEFAULT_DIFFICULTY: str = "beginner"
    DEFAULT_USER_STATUS: str = "active"
    
    # Cache Expiration
    USER_PROFILE_EXPIRE_SECONDS: int = 86400 * 365  # 1 year
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()
