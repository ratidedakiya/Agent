import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Settings:
    """Application settings and configuration"""
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ai_tutor.db")
    
    # Redis (for caching and message queues)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    
    # Audio Processing
    MAX_AUDIO_SIZE_MB: int = int(os.getenv("MAX_AUDIO_SIZE_MB", "10"))
    SUPPORTED_AUDIO_FORMATS: list = ["wav", "mp3", "ogg", "m4a"]
    
    # TTS Configuration
    TTS_PROVIDER: str = os.getenv("TTS_PROVIDER", "openai")
    TTS_MODEL: str = os.getenv("TTS_MODEL", "tts-1")
    
    # Avatar Configuration
    AVATAR_PROVIDER: str = os.getenv("AVATAR_PROVIDER", "local")
    AVATAR_QUALITY: str = os.getenv("AVATAR_QUALITY", "medium")
    
    # Session Configuration
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    MAX_SESSIONS: int = int(os.getenv("MAX_SESSIONS", "1000"))
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # File Upload
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Monitoring
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "True").lower() == "true"
    METRICS_PORT: int = int(os.getenv("METRICS_PORT", "9090"))
    
    # Feature Flags
    ENABLE_AVATAR: bool = os.getenv("ENABLE_AVATAR", "True").lower() == "true"
    ENABLE_STREAMING: bool = os.getenv("ENABLE_STREAMING", "True").lower() == "true"
    ENABLE_QUIZ: bool = os.getenv("ENABLE_QUIZ", "True").lower() == "true"
    ENABLE_HOMEWORK_CHECK: bool = os.getenv("ENABLE_HOMEWORK_CHECK", "True").lower() == "true"
    
    # Performance
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "100"))
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    
    # Language Support
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "en")
    SUPPORTED_LANGUAGES: list = os.getenv("SUPPORTED_LANGUAGES", "en,hi,gu,es,fr").split(",")
    
    # Voice Configuration
    DEFAULT_VOICE_STYLE: str = os.getenv("DEFAULT_VOICE_STYLE", "friendly_male")
    VOICE_SPEED: float = float(os.getenv("VOICE_SPEED", "1.0"))
    VOICE_PITCH: float = float(os.getenv("VOICE_PITCH", "1.0"))
    
    # Avatar Configuration
    DEFAULT_AVATAR_TEMPLATE: str = os.getenv("DEFAULT_AVATAR_TEMPLATE", "teacher_1")
    AVATAR_RENDER_QUALITY: str = os.getenv("AVATAR_RENDER_QUALITY", "medium")
    
    # Cache Configuration
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "300"))
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "True").lower() == "true"
    
    # Error Handling
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY_SECONDS: int = int(os.getenv("RETRY_DELAY_SECONDS", "1"))
    
    # Development
    RELOAD: bool = os.getenv("RELOAD", "False").lower() == "true"
    WORKERS: int = int(os.getenv("WORKERS", "1"))
    
    def __init__(self):
        """Initialize settings and validate configuration"""
        self._validate_settings()
    
    def _validate_settings(self):
        """Validate required settings"""
        if not self.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set. Some features may not work.")
        
        if not self.SECRET_KEY or self.SECRET_KEY == "your-secret-key-here":
            print("Warning: SECRET_KEY not set or using default. This is not secure for production.")
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
    
    def get_database_url(self) -> str:
        """Get database URL with proper formatting"""
        if self.DATABASE_URL.startswith("sqlite"):
            return self.DATABASE_URL
        else:
            # Add connection pooling for production databases
            return f"{self.DATABASE_URL}?pool_size=10&max_overflow=20"
    
    def get_redis_url(self) -> str:
        """Get Redis URL with proper formatting"""
        return self.REDIS_URL
    
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.DEBUG or self.RELOAD
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.is_development()
    
    def get_cors_origins(self) -> list:
        """Get CORS allowed origins"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS if origin.strip()]
    
    def get_supported_audio_formats(self) -> list:
        """Get supported audio formats"""
        return [fmt.strip().lower() for fmt in self.SUPPORTED_AUDIO_FORMATS if fmt.strip()]
    
    def get_supported_languages(self) -> list:
        """Get supported languages"""
        return [lang.strip().lower() for lang in self.SUPPORTED_LANGUAGES if lang.strip()]

# Create global settings instance
settings = Settings()