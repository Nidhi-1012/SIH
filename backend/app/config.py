import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Look for .env in current directory or parent directory
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if not env_path.exists():
    env_path = Path(".env")
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    PROJECT_NAME: str = "NER-LINK AI — Smart Logistics & Accessibility Intelligence"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database (Defaults to PostgreSQL in Docker, fallback to SQLite)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres_secure_password@localhost:5432/ner_link_db"
    )
    
    # Supabase (Authentication)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    # Server-side only. Never expose to frontend/browser code.
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    # Shared secret gating officer self-signup. Give this to real officers only,
    # out of band (not committed, not shown in the UI).
    OFFICER_INVITE_CODE: str = os.getenv("OFFICER_INVITE_CODE", "")

    # External APIs
    IMD_API_KEY: str = os.getenv("IMD_API_KEY", "")
    IMD_API_ENDPOINT: str = os.getenv("IMD_API_ENDPOINT", "https://api.imd.gov.in/v1")
    BHUVAN_API_KEY: str = os.getenv("BHUVAN_API_KEY", "")
    BHUVAN_TILE_URL: str = os.getenv("BHUVAN_TILE_URL", "https://bhuvan-vec1.nrsc.gov.in/bhuvan/gwc/service/wmts")
    
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"
    GRAPHHOPPER_URL: str = os.getenv("GRAPHHOPPER_URL", "http://localhost:8989")
    
    model_config = SettingsConfigDict(case_sensitive=True, env_file=str(env_path), extra="ignore")

settings = Settings()
