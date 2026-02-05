"""
Health check and system status endpoints.
"""
import logging
from fastapi import APIRouter

from app.models.schemas import HealthResponse
from app.services.search_service import search_service
from app.core.embedding import embedding_generator
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["System"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check system health and get statistics"
)
async def health_check():
    """
    Return system health status and statistics.
    
    Includes:
    - Application version
    - Embedding model info
    - Database statistics
    - Configuration details
    """
    try:
        # Get database stats
        stats = search_service.get_stats()
        
        # Get model info
        model_info = embedding_generator.get_model_info()
        
        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            embedding_model=model_info['model_name'],
            vector_store="chromadb",
            total_documents=stats.get('total_documents', 0),
            total_chunks=stats.get('total_chunks', 0)
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="degraded",
            version=settings.app_version,
            embedding_model="unknown",
            total_documents=0,
            total_chunks=0
        )


@router.get(
    "/stats",
    summary="System statistics",
    description="Get detailed system statistics"
)
async def get_statistics():
    """Get detailed statistics about the system."""
    try:
        db_stats = search_service.get_stats()
        model_info = embedding_generator.get_model_info()
        
        return {
            "database": db_stats,
            "embedding_model": model_info,
            "configuration": {
                "chunk_size": settings.chunk_size,
                "chunk_overlap": settings.chunk_overlap,
                "search_top_k": settings.search_top_k,
                "embedding_dimension": settings.embedding_dimension
            }
        }
        
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        return {"error": str(e)}
