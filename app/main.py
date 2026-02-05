"""
FastAPI application entry point.
Configures routes, middleware, and startup/shutdown events.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.utils.logger import setup_logging
from app.api.routes import ingest, query, health


# Initialize logging
setup_logging(log_level="DEBUG" if settings.debug else "INFO")
logger = logging.getLogger(__name__)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Handles resource initialization and cleanup.
    """
    # Startup
    logger.info("=" * 80)
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info("=" * 80)
    
    # Warm up embedding model (loads model into memory)
    logger.info("Loading embedding model...")
    from app.core.embedding import embedding_generator
    try:
        _ = embedding_generator.embed_text("warmup")
        logger.info("✓ Embedding model loaded successfully")
    except Exception as e:
        logger.error(f"✗ Failed to load embedding model: {e}")
        raise
    
    # Initialize vector database connection
    logger.info("Connecting to vector database...")
    from app.services.search_service import search_service
    stats = search_service.get_stats()
    logger.info(f"✓ Vector database connected: {stats}")
    
    logger.info("=" * 80)
    logger.info("Application ready to receive requests")
    logger.info(f"API: http://{settings.api_host}:{settings.api_port}")
    logger.info(f"Docs: http://{settings.api_host}:{settings.api_port}/docs")
    logger.info("=" * 80)
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    logger.info("Cleanup complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    AI-Powered Research Assistant API
    
    A production-grade RAG (Retrieval-Augmented Generation) system for semantic document search.
    
    ## Features
    - Document ingestion with semantic chunking
    - Vector embeddings using sentence-transformers
    - Semantic search with ChromaDB
    - Extractive summarization
    - RESTful API with automatic documentation
    
    ## Workflow
    1. **Ingest**: Upload documents via `/ingest/text` or `/ingest/file`
    2. **Query**: Search documents using `/query/search`
    3. **Monitor**: Check system health at `/health`
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (configure as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(ingest.router)
app.include_router(query.router)

# Serve the web UI
@app.get("/ui")
async def get_ui():
    """Serve the web interface."""
    return FileResponse("index.html")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Catch-all exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "ingest_text": "/ingest/text",
            "ingest_file": "/ingest/file",
            "search": "/query/search"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        workers=settings.api_workers
    )
