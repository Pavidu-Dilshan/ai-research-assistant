"""
Pydantic models for request/response validation and serialization.
Ensures type safety and automatic API documentation.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Document Schemas
# ============================================================================

class DocumentMetadata(BaseModel):
    """Metadata associated with an ingested document."""
    source: str = Field(..., description="Original filename or source identifier")
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    total_chunks: int = Field(..., ge=1, description="Number of chunks created")
    file_size_bytes: Optional[int] = None
    content_type: str = "text/plain"


class DocumentIngestRequest(BaseModel):
    """Request model for document ingestion."""
    content: str = Field(..., min_length=1, description="Raw document text")
    filename: str = Field(..., min_length=1, description="Document identifier")
    metadata: Optional[dict] = Field(default_factory=dict)


class DocumentIngestResponse(BaseModel):
    """Response after successful document ingestion."""
    document_id: str = Field(..., description="Unique document identifier")
    chunks_created: int = Field(..., ge=1)
    embedding_dimension: int
    message: str = "Document ingested successfully"


# ============================================================================
# Chunk Schemas
# ============================================================================

class DocumentChunk(BaseModel):
    """Represents a single chunk of a document with embedding."""
    chunk_id: str = Field(default_factory=lambda: str(uuid4()))
    document_id: str
    chunk_index: int = Field(..., ge=0)
    text: str = Field(..., min_length=1)
    start_char: int = Field(..., ge=0)
    end_char: int = Field(..., ge=1)
    
    @field_validator('end_char')
    @classmethod
    def validate_char_range(cls, v, info):
        if 'start_char' in info.data and v <= info.data['start_char']:
            raise ValueError("end_char must be greater than start_char")
        return v


# ============================================================================
# Search Schemas
# ============================================================================

class SearchResult(BaseModel):
    """Single search result with relevance information."""
    chunk_id: str
    document_id: str
    text: str
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    metadata: dict = Field(default_factory=dict)


class QueryRequest(BaseModel):
    """Request model for semantic search queries."""
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    score_threshold: float = Field(default=0.3, ge=0.0, le=1.0)
    include_summary: bool = Field(default=True)


class QueryResponse(BaseModel):
    """Response for search queries with results and optional summary."""
    query: str
    results: List[SearchResult]
    total_results: int
    summary: Optional[str] = None
    processing_time_ms: float


# ============================================================================
# Health & System Schemas
# ============================================================================

class HealthResponse(BaseModel):
    """System health status."""
    status: str = "healthy"
    version: str
    embedding_model: str
    vector_store: str = "chromadb"
    total_documents: int
    total_chunks: int


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
