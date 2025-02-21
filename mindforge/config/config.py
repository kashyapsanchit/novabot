
from pydantic_settings import BaseSettings
from qdrant_client import QdrantClient
from functools import lru_cache
from langchain_groq import ChatGroq


class Settings(BaseSettings):
    QDRANT_HOST: str = "localhost"
    QDRANT_KEY: str 
    GROQ_KEY: str 
    MODEL: str = "llama-3.1-8b-instant"

    class Config:
        env_file = ".env"
        

@lru_cache()
def get_qdrant_client() -> QdrantClient:

    settings = Settings()
    return QdrantClient(
        url=settings.QDRANT_HOST,
        api_key=settings.QDRANT_KEY,
        timeout=30
    )

@lru_cache()
def get_llm():
    settings = Settings()
    llm = ChatGroq(
        model=settings.MODEL,
        api_key=settings.GROQ_KEY
    )
    return llm 