from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str = "philly-restaurants"
    PINECONE_NAMESPACE: str = "philadelphia-food"
    MAX_CONCURRENT_REQUESTS: int = 5

    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        extra = "ignore"
    
settings = Settings()