from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings and configuration
    Load from enviroment variables or .env file
    """
    
    # Application
    APP_NAME: str = "AI-Powered Menu Pricing System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/pricing_db"
    
    # External APIs
    OPENWEATHER_API_KEY: Optional[str] = None
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5"
    
    TICKETMASTER_API_KEY: Optional[str] = None
    TICKETMASTER_BASE_URL: str = "https://app.ticketmaster.com/discovery/v2"
    
    # Pricing Engine Configuration
    INTERNAL_WEIGHT: float = 0.6
    EXTERNAL_WEIGHT: float = 0.4
    
    # Cache Configuration
    WEATHER_CACHE_MINUTES: int = 30
    EVENT_CACHE_HOURS: int = 6
    
    # API Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()