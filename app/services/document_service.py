"""
Document service handling ingestion, validation, and storage.
Orchestrates chunking, embedding, and vector storage.
"""
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import logging
from uuid import uuid4

from app.models.schemas import (
    DocumentChunk,
    DocumentIngestRequest,
    DocumentIngestResponse,
    DocumentMetadata
)
from app.core.chunking import SemanticChunker
from app.core.embedding import embedding_generator
from app.config import settings

logger = logging.getLogger(__name__)


class DocumentService:
    """
    High-level service for document management.
    
    Responsibilities:
    - Validate and process document inputs
    - Coordinate chunking pipeline
    - Generate embeddings for chunks
    - Prepare data for vector storage
    """
    
    def __init__(self):
        self.chunker = SemanticChunker(
            chunk_size=settings.chunk_size,
            overlap=settings.chunk_overlap
        )
    
    async def ingest_document(
        self,
        request: DocumentIngestRequest
    ) -> tuple[str, List[DocumentChunk], List[List[float]]]:
        """
        Process a document through the full ingestion pipeline.
        
        Args:
            request: Document ingestion request
            
        Returns:
            Tuple of (document_id, chunks, embeddings)
            
        Raises:
            ValueError: If document validation fails
            RuntimeError: If processing fails
        """
        # Validate input
        self._validate_document(request)
        
        # Generate unique document ID
        document_id = self._generate_document_id(request.filename)
        
        logger.info(
            f"Ingesting document: {request.filename} "
            f"({len(request.content)} chars) as {document_id}"
        )
        
        try:
            # Step 1: Chunk the document
            chunks = self.chunker.chunk_text(request.content, document_id)
            logger.info(f"Created {len(chunks)} chunks for {document_id}")
            
            # Step 2: Generate embeddings for all chunks
            chunk_texts = [chunk.text for chunk in chunks]
            embeddings = embedding_generator.embed_batch(
                chunk_texts,
                show_progress=len(chunk_texts) > 50
            )
            
            # Convert numpy array to list for ChromaDB
            embeddings_list = embeddings.tolist()
            
            logger.info(
                f"Generated {len(embeddings_list)} embeddings "
                f"(dim={len(embeddings_list[0])})"
            )
            
            # Log chunk statistics
            stats = self.chunker.get_chunk_stats(chunks)
            logger.debug(f"Chunk stats for {document_id}: {stats}")
            
            return document_id, chunks, embeddings_list
            
        except Exception as e:
            logger.error(f"Document ingestion failed for {document_id}: {e}")
            raise RuntimeError(f"Failed to process document: {e}")
    
    def _validate_document(self, request: DocumentIngestRequest):
        """Validate document before processing."""
        # Check content size
        content_size_mb = len(request.content.encode('utf-8')) / (1024 * 1024)
        if content_size_mb > settings.max_file_size_mb:
            raise ValueError(
                f"Document too large: {content_size_mb:.2f}MB "
                f"(max: {settings.max_file_size_mb}MB)"
            )
        
        # Check content is not empty
        if not request.content.strip():
            raise ValueError("Document content cannot be empty")
        
        # Check filename is valid
        if not request.filename or len(request.filename) > 255:
            raise ValueError("Invalid filename")
    
    def _generate_document_id(self, filename: str) -> str:
        """Generate a unique, sortable document ID."""
        # Use timestamp + uuid for uniqueness and sortability
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid4())[:8]
        
        # Sanitize filename
        safe_filename = "".join(
            c for c in filename if c.isalnum() or c in "._-"
        )[:50]
        
        return f"{timestamp}_{safe_filename}_{unique_id}"
    
    def create_metadata(
        self,
        document_id: str,
        filename: str,
        num_chunks: int,
        content_size: int
    ) -> DocumentMetadata:
        """Create metadata object for a processed document."""
        return DocumentMetadata(
            source=filename,
            total_chunks=num_chunks,
            file_size_bytes=content_size,
            ingested_at=datetime.utcnow()
        )


# Global service instance
document_service = DocumentService()
