"""
API routes for document ingestion with PDF support.
"""
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from app.models.schemas import (
    DocumentIngestRequest,
    DocumentIngestResponse,
    ErrorResponse
)
from app.services.document_service import document_service
from app.services.search_service import search_service
from app.utils.pdf_processor import pdf_processor
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ingest", tags=["Document Ingestion"])


@router.post(
    "/text",
    response_model=DocumentIngestResponse,
    status_code=201,
    summary="Ingest text document",
    description="Process and store a text document for semantic search"
)
async def ingest_text_document(request: DocumentIngestRequest):
    """
    Ingest a text document into the system.
    
    Workflow:
    1. Validate document
    2. Chunk text into semantic segments
    3. Generate embeddings for each chunk
    4. Store chunks and embeddings in vector database
    """
    try:
        # Process document through ingestion pipeline
        document_id, chunks, embeddings = await document_service.ingest_document(request)
        
        # Create metadata
        metadata = document_service.create_metadata(
            document_id=document_id,
            filename=request.filename,
            num_chunks=len(chunks),
            content_size=len(request.content.encode('utf-8'))
        )
        
        # Store in vector database
        await search_service.store_chunks(
            document_id=document_id,
            chunks=chunks,
            embeddings=embeddings,
            metadata=metadata.model_dump()
        )
        
        return DocumentIngestResponse(
            document_id=document_id,
            chunks_created=len(chunks),
            embedding_dimension=settings.embedding_dimension,
            message=f"Document '{request.filename}' ingested successfully"
        )
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Document ingestion failed: {str(e)}"
        )


@router.post(
    "/file",
    response_model=DocumentIngestResponse,
    status_code=201,
    summary="Ingest file upload",
    description="Upload and process a text or PDF file"
)
async def ingest_file(
    file: UploadFile = File(..., description="File to ingest (.txt, .md, .pdf)")
):
    """
    Ingest a document from file upload.
    Supports: .txt, .md, .pdf
    """
    # Validate file type
    allowed_extensions = {'.txt', '.md', '.pdf'}
    file_extension = None
    if file.filename:
        file_extension = '.' + file.filename.split('.')[-1].lower()
    
    if not file_extension or file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {allowed_extensions}"
        )
    
    try:
        # Read file content
        content_bytes = await file.read()
        
        # Extract text based on file type
        if file_extension == '.pdf':
            logger.info(f"Processing PDF file: {file.filename}")
            text_content = pdf_processor.extract_text_from_bytes(content_bytes)
        else:
            # Text file
            text_content = content_bytes.decode('utf-8')
        
        # Create request and process
        request = DocumentIngestRequest(
            content=text_content,
            filename=file.filename or "uploaded_file.txt"
        )
        
        return await ingest_text_document(request)
        
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Text file must be valid UTF-8 encoded"
        )
    except ValueError as e:
        # PDF processing error
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"File ingestion failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"File processing failed: {str(e)}"
        )


@router.delete(
    "/documents/{document_id}",
    status_code=200,
    summary="Delete document",
    description="Remove a document and all its chunks from the system"
)
async def delete_document(document_id: str):
    """Delete a document by ID."""
    try:
        await search_service.delete_document(document_id)
        return {"message": f"Document {document_id} deleted successfully"}
        
    except Exception as e:
        logger.error(f"Document deletion failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        )


@router.get(
    "/documents",
    status_code=200,
    summary="List all documents",
    description="Get a list of all ingested documents"
)
async def list_documents():
    """List all documents in the system."""
    try:
        stats = search_service.get_stats()
        
        # Get all unique documents
        all_items = search_service._collection.get()
        
        documents = {}
        if all_items['metadatas']:
            for metadata in all_items['metadatas']:
                doc_id = metadata['document_id']
                if doc_id not in documents:
                    documents[doc_id] = {
                        "document_id": doc_id,
                        "source": metadata.get('source', 'Unknown'),
                        "chunk_count": 0,
                        "ingested_at": metadata.get('ingested_at', 'Unknown')
                    }
                documents[doc_id]['chunk_count'] += 1
        
        return {
            "total_documents": len(documents),
            "total_chunks": stats['total_chunks'],
            "documents": list(documents.values())
        }
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.post(
    "/reset",
    status_code=200,
    summary="Reset database (DANGER)",
    description="Delete all documents and embeddings. Use with caution."
)
async def reset_database():
    """Reset the entire vector database (destructive operation)."""
    try:
        await search_service.reset_database()
        return {
            "message": "Database reset successfully",
            "warning": "All documents and embeddings have been deleted"
        }
        
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset database: {str(e)}"
        )
