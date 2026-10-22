from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str = "philly-restaurants"
    PINECONE_NAMESPACE: str = "philadelphia-food"
    MAX_CONCURRENT_REQUESTS: int = 5

    class Config:
        env_file = ".env"
    
settings = Settings()