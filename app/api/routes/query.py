"""
API routes for semantic search and document retrieval.
"""
import logging
import time
from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import QueryRequest, QueryResponse, SearchResult
from app.services.search_service import search_service
from app.core.summarization import extractive_summarizer
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/query", tags=["Search & Query"])


@router.post(
    "/search",
    response_model=QueryResponse,
    summary="Semantic search",
    description="Search documents using natural language queries"
)
async def semantic_search(request: QueryRequest):
    """
    Perform semantic search over ingested documents.
    
    Workflow:
    1. Generate query embedding
    2. Find most similar document chunks
    3. Optionally generate extractive summary
    4. Return ranked results
    """
    start_time = time.time()
    
    try:
        # Perform vector search
        results = await search_service.search(
            query=request.query,
            top_k=request.top_k,
            score_threshold=request.score_threshold
        )
        
        # Generate summary if requested
        summary = None
        if request.include_summary and results:
            try:
                retrieved_texts = [r.text for r in results]
                summary = extractive_summarizer.summarize(
                    query=request.query,
                    retrieved_texts=retrieved_texts
                )
            except Exception as e:
                logger.warning(f"Summarization failed: {e}")
                summary = "Summary generation failed"
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        return QueryResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            summary=summary,
            processing_time_ms=processing_time_ms
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Search operation failed: {str(e)}"
        )


@router.get(
    "/documents/{document_id}",
    response_model=list[SearchResult],
    summary="Get document chunks",
    description="Retrieve all chunks for a specific document"
)
async def get_document_chunks(document_id: str):
    """Retrieve all chunks associated with a document ID."""
    try:
        chunks = await search_service.get_document_chunks(document_id)
        
        if not chunks:
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} not found"
            )
        
        return chunks
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document retrieval failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve document: {str(e)}"
        )


@router.get(
    "/similar/{chunk_id}",
    response_model=list[SearchResult],
    summary="Find similar chunks",
    description="Find chunks similar to a given chunk"
)
async def find_similar_chunks(
    chunk_id: str,
    top_k: int = Query(default=5, ge=1, le=20)
):
    """
    Find chunks similar to a specific chunk.
    Useful for exploring related content.
    """
    try:
        # Get the target chunk
        # This is a simplified implementation
        # In production, you'd store chunk embeddings separately for direct access
        
        raise HTTPException(
            status_code=501,
            detail="Similar chunk search not yet implemented in Phase 1"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Similar chunk search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )
