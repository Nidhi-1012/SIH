import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "NER-LINK AI — Smart Logistics & Accessibility Intelligence"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./data/ner_link.db"
    )
    
    # External APIs
    IMD_API_KEY: str = os.getenv("IMD_API_KEY", "")
    IMD_API_ENDPOINT: str = os.getenv("IMD_API_ENDPOINT", "https://api.imd.gov.in/v1")
    BHUVAN_API_KEY: str = os.getenv("BHUVAN_API_KEY", "")
    BHUVAN_TILE_URL: str = os.getenv("BHUVAN_TILE_URL", "https://bhuvan-vec1.nrsc.gov.in/bhuvan/gwc/service/wmts")
    
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"
    GRAPHHOPPER_URL: str = os.getenv("GRAPHHOPPER_URL", "http://localhost:8989")
    
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

settings = Settings()
