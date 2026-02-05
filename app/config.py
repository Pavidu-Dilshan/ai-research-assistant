"""
Application configuration management using pydantic-settings.
Supports environment variables and .env files.
"""
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation and type safety."""
    
    # Application
    app_name: str = "AI Research Assistant"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent
    data_dir: Path = base_dir / "data"
    documents_dir: Path = data_dir / "documents"
    chroma_dir: Path = data_dir / "chroma_db"
    
    # Embedding Model
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384  # Dimension for all-MiniLM-L6-v2
    embedding_batch_size: int = 32
    embedding_device: str = "cpu"  # "cuda" if GPU available
    
    # ChromaDB
    chroma_collection_name: str = "research_documents"
    
    # Document Processing
    chunk_size: int = 512  # Characters per chunk
    chunk_overlap: int = 128  # Overlap between chunks
    max_file_size_mb: int = 50
    
    # Search
    search_top_k: int = 5  # Number of chunks to retrieve
    search_score_threshold: float = 0.3  # Minimum similarity score
    
    # Summarization
    summary_max_sentences: int = 3
    summary_compression_ratio: float = 0.3
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
