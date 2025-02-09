from pydantic_settings import BaseSettings
from qdrant_client import QdrantClient
from functools import lru_cache

class Settings(BaseSettings):
    QDRANT_HOST: str = "localhost"
    QDRANT_KEY: str = "default"
    
    class Config:
        env_file = ".env"
        

@lru_cache()
def get_qdrant_client() -> QdrantClient:

    settings = Settings()
    return QdrantClient(
        url=settings.QDRANT_HOST,
        api_key=settings.QDRANT_KEY
    )