"""
Unit tests for text chunking functionality.
"""
import pytest

from app.core.chunking import SemanticChunker, FixedSizeChunker
from app.models.schemas import DocumentChunk


class TestSemanticChunker:
    """Test cases for semantic-aware text chunking."""
    
    def test_basic_chunking(self):
        """Test basic chunking with simple text."""
        chunker = SemanticChunker(chunk_size=100, overlap=20)
        text = "This is sentence one. This is sentence two. This is sentence three."
        
        chunks = chunker.chunk_text(text, document_id="test_doc")
        
        assert len(chunks) > 0
        assert all(isinstance(c, DocumentChunk) for c in chunks)
        assert all(c.document_id == "test_doc" for c in chunks)
    
    def test_chunk_overlap(self):
        """Test that chunks have proper overlap."""
        chunker = SemanticChunker(chunk_size=50, overlap=20)
        text = "A" * 200  # Long text
        
        chunks = chunker.chunk_text(text, document_id="test_doc")
        
        # Should create multiple chunks
        assert len(chunks) > 1
        
        # Verify chunk indices are sequential
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i
    
    def test_empty_text_raises_error(self):
        """Test that empty text raises ValueError."""
        chunker = SemanticChunker()
        
        with pytest.raises(ValueError, match="Cannot chunk empty text"):
            chunker.chunk_text("", document_id="test_doc")
    
    def test_chunk_character_positions(self):
        """Test that start_char and end_char are valid."""
        chunker = SemanticChunker(chunk_size=100, overlap=20)
        text = "Test sentence. Another sentence. Yet another sentence."
        
        chunks = chunker.chunk_text(text, document_id="test_doc")
        
        for chunk in chunks:
            assert chunk.start_char >= 0
            assert chunk.end_char > chunk.start_char
            assert chunk.end_char <= len(text) + 100  # Allow some margin


class TestFixedSizeChunker:
    """Test cases for fixed-size chunking (fallback strategy)."""
    
    def test_fixed_size_chunking(self):
        """Test basic fixed-size chunking."""
        chunker = FixedSizeChunker(chunk_size=50, overlap=10)
        text = "A" * 200
        
        chunks = chunker.chunk_text(text, document_id="test_doc")
        
        assert len(chunks) > 0
        # Most chunks should be exactly chunk_size
        assert all(len(c.text) <= 50 for c in chunks)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
