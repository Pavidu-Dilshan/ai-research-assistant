"""
Embedding generation using sentence-transformers.
Implements model caching, batch processing, and error handling.
"""
from typing import List, Optional
import logging

import numpy as np
from sentence_transformers import SentenceTransformer
import torch

from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Generates dense vector embeddings for text using sentence-transformers.
    
    Features:
    - Lazy model loading (singleton pattern)
    - Batch processing for efficiency
    - GPU acceleration if available
    - Normalized embeddings for cosine similarity
    """
    
    _instance: Optional['EmbeddingGenerator'] = None
    _model: Optional[SentenceTransformer] = None
    
    def __new__(cls):
        """Singleton pattern to avoid loading model multiple times."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize embedding generator (model loaded lazily)."""
        if self._model is None:
            self._load_model()
    
    def _load_model(self):
        """Load the sentence-transformer model."""
        try:
            logger.info(f"Loading embedding model: {settings.embedding_model_name}")
            
            # Check device availability
            device = settings.embedding_device
            if device == "cuda" and not torch.cuda.is_available():
                logger.warning("CUDA requested but not available. Falling back to CPU.")
                device = "cpu"
            
            self._model = SentenceTransformer(
                settings.embedding_model_name,
                device=device
            )
            
            # Verify model dimension matches config
            test_embedding = self._model.encode("test", convert_to_numpy=True)
            actual_dim = test_embedding.shape[0]
            
            if actual_dim != settings.embedding_dimension:
                logger.warning(
                    f"Model dimension mismatch: expected {settings.embedding_dimension}, "
                    f"got {actual_dim}. Updating config."
                )
                settings.embedding_dimension = actual_dim
            
            logger.info(
                f"Model loaded successfully. "
                f"Device: {device}, Dimension: {settings.embedding_dimension}"
            )
            
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise RuntimeError(f"Could not initialize embedding model: {e}")
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text string.
        
        Args:
            text: Input text to embed
            
        Returns:
            Normalized embedding vector
        """
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text")
        
        return self.embed_batch([text])[0]
    
    def embed_batch(
        self,
        texts: List[str],
        batch_size: Optional[int] = None,
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of text strings to embed
            batch_size: Processing batch size (uses config default if None)
            show_progress: Show progress bar for large batches
            
        Returns:
            Array of normalized embeddings (shape: [n_texts, embedding_dim])
        """
        if not texts:
            raise ValueError("Cannot embed empty text list")
        
        if any(not t or not t.strip() for t in texts):
            raise ValueError("Text list contains empty strings")
        
        batch_size = batch_size or settings.embedding_batch_size
        
        try:
            embeddings = self._model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
                normalize_embeddings=True  # L2 normalization for cosine similarity
            )
            
            logger.debug(f"Generated {len(texts)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise RuntimeError(f"Failed to generate embeddings: {e}")
    
    def compute_similarity(
        self,
        query_embedding: np.ndarray,
        document_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Compute cosine similarity between query and document embeddings.
        
        Args:
            query_embedding: Single query embedding vector
            document_embeddings: Array of document embeddings
            
        Returns:
            Similarity scores (higher = more similar)
        """
        # Since embeddings are normalized, dot product = cosine similarity
        similarities = np.dot(document_embeddings, query_embedding)
        return similarities
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model."""
        return {
            "model_name": settings.embedding_model_name,
            "embedding_dimension": settings.embedding_dimension,
            "device": str(self._model.device) if self._model else "not loaded",
            "max_seq_length": self._model.max_seq_length if self._model else None
        }
    
    @property
    def model(self) -> SentenceTransformer:
        """Access underlying model (for advanced use cases)."""
        if self._model is None:
            self._load_model()
        return self._model


# Global singleton instance
embedding_generator = EmbeddingGenerator()
