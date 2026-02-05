"""
Text chunking strategies for document processing.
Implements semantic-aware chunking with overlap for context preservation.
"""
import re
from typing import List, Tuple

from app.models.schemas import DocumentChunk


class SemanticChunker:
    """
    Chunks text with semantic awareness (sentence boundaries) and overlap.
    
    Strategy:
    1. Split on sentence boundaries (., !, ?)
    2. Combine sentences up to max_chunk_size
    3. Add overlap by including sentences from previous chunk
    4. Preserve context across chunk boundaries
    """
    
    def __init__(self, chunk_size: int = 512, overlap: int = 128):
        """
        Args:
            chunk_size: Target characters per chunk (soft limit)
            overlap: Characters to overlap between chunks
        """
        if overlap >= chunk_size:
            raise ValueError("Overlap must be smaller than chunk_size")
        
        self.chunk_size = chunk_size
        self.overlap = overlap
        
        # Sentence boundary pattern (handles common abbreviations)
        self.sentence_pattern = re.compile(
            r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s',
            re.MULTILINE
        )
    
    def chunk_text(self, text: str, document_id: str) -> List[DocumentChunk]:
        """
        Split text into overlapping chunks at sentence boundaries.
        
        Args:
            text: Input text to chunk
            document_id: Identifier for the parent document
            
        Returns:
            List of DocumentChunk objects with metadata
        """
        if not text or not text.strip():
            raise ValueError("Cannot chunk empty text")
        
        # Normalize whitespace
        text = self._normalize_text(text)
        
        # Split into sentences
        sentences = self.sentence_pattern.split(text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            # Fallback: treat entire text as one sentence
            sentences = [text]
        
        chunks = []
        current_chunk = []
        current_length = 0
        chunk_index = 0
        start_char = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # If adding this sentence exceeds chunk_size, finalize current chunk
            if current_chunk and current_length + sentence_length > self.chunk_size:
                chunk_text = ' '.join(current_chunk)
                end_char = start_char + len(chunk_text)
                
                chunks.append(DocumentChunk(
                    document_id=document_id,
                    chunk_index=chunk_index,
                    text=chunk_text,
                    start_char=start_char,
                    end_char=end_char
                ))
                
                # Calculate overlap: take last sentences that fit in overlap window
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = [s for s in overlap_text.split('. ') if s.strip()]
                current_length = len(overlap_text)
                start_char = end_char - current_length
                chunk_index += 1
            
            current_chunk.append(sentence)
            current_length += sentence_length + 1  # +1 for space
        
        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            end_char = start_char + len(chunk_text)
            
            chunks.append(DocumentChunk(
                document_id=document_id,
                chunk_index=chunk_index,
                text=chunk_text,
                start_char=start_char,
                end_char=end_char
            ))
        
        return chunks
    
    def _normalize_text(self, text: str) -> str:
        """Normalize whitespace while preserving sentence structure."""
        # Replace multiple spaces/newlines with single space
        text = re.sub(r'\s+', ' ', text)
        # Ensure space after sentence endings
        text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
        return text.strip()
    
    def _get_overlap_text(self, sentences: List[str]) -> str:
        """
        Get last N sentences that fit within overlap window.
        
        Args:
            sentences: List of sentences in current chunk
            
        Returns:
            String containing overlap text
        """
        overlap_sentences = []
        overlap_length = 0
        
        # Work backwards from end of chunk
        for sentence in reversed(sentences):
            sentence_length = len(sentence) + 1  # +1 for space
            if overlap_length + sentence_length > self.overlap:
                break
            overlap_sentences.insert(0, sentence)
            overlap_length += sentence_length
        
        return ' '.join(overlap_sentences)
    
    def get_chunk_stats(self, chunks: List[DocumentChunk]) -> dict:
        """Calculate statistics about chunks for debugging/monitoring."""
        if not chunks:
            return {"error": "No chunks provided"}
        
        lengths = [len(c.text) for c in chunks]
        return {
            "total_chunks": len(chunks),
            "avg_chunk_length": sum(lengths) / len(lengths),
            "min_chunk_length": min(lengths),
            "max_chunk_length": max(lengths),
            "total_characters": sum(lengths)
        }


class FixedSizeChunker:
    """
    Simple fixed-size chunker (fallback strategy).
    Splits text at exact character boundaries with overlap.
    """
    
    def __init__(self, chunk_size: int = 512, overlap: int = 128):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, document_id: str) -> List[DocumentChunk]:
        """Split text into fixed-size chunks with overlap."""
        if not text or not text.strip():
            raise ValueError("Cannot chunk empty text")
        
        text = text.strip()
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            chunks.append(DocumentChunk(
                document_id=document_id,
                chunk_index=chunk_index,
                text=chunk_text,
                start_char=start,
                end_char=end
            ))
            
            start += self.chunk_size - self.overlap
            chunk_index += 1
        
        return chunks
