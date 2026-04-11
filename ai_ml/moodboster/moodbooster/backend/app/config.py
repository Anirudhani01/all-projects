from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "MoodBooster API"
    debug: bool = False
    database_url: str = "mysql+pymysql://anirudh:password123@localhost:3306/moodbooster"
    
    # AI/ML Settings
    huggingface_model: str = "distilbert-base-uncased-finetuned-sst-2-english"
    spacy_model: str = "en_core_web_sm"
    
    # LLM Settings
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-1.5-flash"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "phi3:mini"
    
    # Fallback settings
    use_gemini: bool = True
    use_ollama: bool = True
    use_keyword_fallback: bool = True
    
    # External API Settings
    # Spotify API
    spotify_client_id: Optional[str] = None
    spotify_client_secret: Optional[str] = None
    
    # YouTube API
    youtube_api_key: Optional[str] = None
    
    # ZenQuotes API (no key required)
    zenquotes_enabled: bool = True
    
    # API Usage Settings
    use_external_apis: bool = True
    api_fallback_enabled: bool = True
    api_rate_limit_buffer: int = 10  # Buffer before rate limit
    
    class Config:
        env_file = ".env"

settings = Settings()
