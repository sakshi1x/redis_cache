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
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()
