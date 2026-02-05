"""
Search service managing vector storage and retrieval with ChromaDB.
Handles semantic search and result ranking.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.models.schemas import SearchResult, DocumentChunk
from app.core.embedding import embedding_generator
from app.config import settings

logger = logging.getLogger(__name__)


class SearchService:
    """
    Vector search service using ChromaDB.
    
    Responsibilities:
    - Manage ChromaDB collections
    - Store document chunks with embeddings
    - Perform semantic similarity search
    - Rank and filter results
    """
    
    def __init__(self):
        self._client: Optional[chromadb.Client] = None
        self._collection = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client and collection."""
        try:
            logger.info(f"Initializing ChromaDB at {settings.chroma_dir}")
            
            # Create persistent client
            self._client = chromadb.PersistentClient(
                path=str(settings.chroma_dir),
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self._collection = self._client.get_or_create_collection(
                name=settings.chroma_collection_name,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
            
            logger.info(
                f"ChromaDB initialized. Collection: {settings.chroma_collection_name}, "
                f"Items: {self._collection.count()}"
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise RuntimeError(f"ChromaDB initialization failed: {e}")
    
    def _serialize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert metadata values to ChromaDB-compatible types.
        ChromaDB only accepts: str, int, float, bool
        """
        serialized = {}
        for key, value in metadata.items():
            if isinstance(value, datetime):
                # Convert datetime to ISO format string
                serialized[key] = value.isoformat()
            elif isinstance(value, (str, int, float, bool)):
                # Already compatible
                serialized[key] = value
            elif value is None:
                # Skip None values
                continue
            else:
                # Convert other types to string
                serialized[key] = str(value)
        return serialized
    
    async def store_chunks(
        self,
        document_id: str,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]],
        metadata: Dict[str, Any]
    ):
        """
        Store document chunks with embeddings in vector database.
        
        Args:
            document_id: Unique document identifier
            chunks: List of document chunks
            embeddings: Corresponding embeddings for each chunk
            metadata: Document-level metadata
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        try:
            # Prepare data for ChromaDB
            ids = [chunk.chunk_id for chunk in chunks]
            texts = [chunk.text for chunk in chunks]
            
            # Serialize document-level metadata
            serialized_metadata = self._serialize_metadata(metadata)
            
            # Add chunk-level metadata
            metadatas = [
                {
                    "document_id": document_id,
                    "chunk_index": chunk.chunk_index,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                    **serialized_metadata  # Include serialized document-level metadata
                }
                for chunk in chunks
            ]
            
            # Store in ChromaDB
            self._collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            
            logger.info(
                f"Stored {len(chunks)} chunks for document {document_id} "
                f"(total items: {self._collection.count()})"
            )
            
        except Exception as e:
            logger.error(f"Failed to store chunks: {e}")
            raise RuntimeError(f"Vector storage failed: {e}")
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.3,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Perform semantic search over stored documents.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            score_threshold: Minimum similarity score (0-1)
            filter_metadata: Optional metadata filters
            
        Returns:
            List of search results ranked by relevance
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        try:
            # Generate query embedding
            query_embedding = embedding_generator.embed_text(query)
            
            # Search in ChromaDB
            results = self._collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
                where=filter_metadata  # Optional metadata filtering
            )
            
            # Parse results
            search_results = []
            
            if results['ids'] and results['ids'][0]:  # Check if results exist
                for i in range(len(results['ids'][0])):
                    # ChromaDB returns distance, convert to similarity score
                    # For cosine distance: similarity = 1 - distance
                    distance = results['distances'][0][i]
                    score = 1 - distance
                    
                    # Apply threshold
                    if score < score_threshold:
                        continue
                    
                    search_results.append(SearchResult(
                        chunk_id=results['ids'][0][i],
                        document_id=results['metadatas'][0][i]['document_id'],
                        text=results['documents'][0][i],
                        score=float(score),
                        metadata=results['metadatas'][0][i]
                    ))
            
            logger.info(
                f"Search query '{query[:50]}...' returned {len(search_results)} results "
                f"(threshold: {score_threshold})"
            )
            
            return search_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise RuntimeError(f"Vector search failed: {e}")
    
    async def get_document_chunks(self, document_id: str) -> List[SearchResult]:
        """Retrieve all chunks for a specific document."""
        try:
            results = self._collection.get(
                where={"document_id": document_id}
            )
            
            search_results = []
            if results['ids']:
                for i in range(len(results['ids'])):
                    search_results.append(SearchResult(
                        chunk_id=results['ids'][i],
                        document_id=document_id,
                        text=results['documents'][i],
                        score=1.0,  # No relevance score for direct retrieval
                        metadata=results['metadatas'][i]
                    ))
            
            return search_results
            
        except Exception as e:
            logger.error(f"Failed to retrieve document chunks: {e}")
            raise RuntimeError(f"Chunk retrieval failed: {e}")
    
    async def delete_document(self, document_id: str):
        """Delete all chunks associated with a document."""
        try:
            # Get all chunk IDs for this document
            results = self._collection.get(
                where={"document_id": document_id}
            )
            
            if results['ids']:
                self._collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} chunks for document {document_id}")
            else:
                logger.warning(f"No chunks found for document {document_id}")
                
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            raise RuntimeError(f"Document deletion failed: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database."""
        try:
            total_items = self._collection.count()
            
            # Get unique document count
            all_items = self._collection.get()
            unique_docs = set()
            if all_items['metadatas']:
                unique_docs = {meta['document_id'] for meta in all_items['metadatas']}
            
            return {
                "total_chunks": total_items,
                "total_documents": len(unique_docs),
                "collection_name": settings.chroma_collection_name,
                "embedding_dimension": settings.embedding_dimension
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}
    
    async def reset_database(self):
        """Delete all data (use with caution)."""
        try:
            self._client.delete_collection(settings.chroma_collection_name)
            self._collection = self._client.create_collection(
                name=settings.chroma_collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.warning("Vector database has been reset")
            
        except Exception as e:
            logger.error(f"Failed to reset database: {e}")
            raise RuntimeError(f"Database reset failed: {e}")


# Global service instance
search_service = SearchService()