from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    APP_NAME: str = "StudioFlowAI"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_HERE"
    
    # LLM API Keys
    GOOGLE_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
