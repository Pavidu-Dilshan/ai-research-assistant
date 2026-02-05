"""
Extractive summarization using query-focused sentence ranking.
Selects most relevant sentences from retrieved chunks.
"""
import re
from typing import List, Tuple
import logging

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.core.embedding import embedding_generator
from app.config import settings

logger = logging.getLogger(__name__)


class ExtractiveSummarizer:
    """
    Query-focused extractive summarization.
    
    Strategy:
    1. Extract sentences from top-k retrieved chunks
    2. Embed all sentences
    3. Rank sentences by similarity to query
    4. Select top-N sentences while avoiding redundancy
    5. Return sentences in original document order
    """
    
    def __init__(
        self,
        max_sentences: int = 3,
        diversity_threshold: float = 0.8
    ):
        """
        Args:
            max_sentences: Maximum sentences in summary
            diversity_threshold: Skip similar sentences above this threshold
        """
        self.max_sentences = max_sentences
        self.diversity_threshold = diversity_threshold
        
        # Sentence splitting pattern
        self.sentence_pattern = re.compile(
            r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s',
            re.MULTILINE
        )
    
    def summarize(
        self,
        query: str,
        retrieved_texts: List[str],
        max_sentences: int = None
    ) -> str:
        """
        Generate query-focused extractive summary.
        
        Args:
            query: User's search query
            retrieved_texts: List of retrieved chunk texts
            max_sentences: Override default max sentences
            
        Returns:
            Summary text with most relevant sentences
        """
        max_sentences = max_sentences or self.max_sentences
        
        if not retrieved_texts:
            return "No relevant content found."
        
        # Extract all sentences with source tracking
        sentences_with_source = []
        for chunk_idx, text in enumerate(retrieved_texts):
            sentences = self._extract_sentences(text)
            for sent_idx, sentence in enumerate(sentences):
                if len(sentence.strip()) > 20:  # Filter very short sentences
                    sentences_with_source.append({
                        'text': sentence,
                        'chunk_idx': chunk_idx,
                        'sent_idx': sent_idx
                    })
        
        if not sentences_with_source:
            return "No suitable sentences found for summarization."
        
        # Embed query and sentences
        try:
            query_embedding = embedding_generator.embed_text(query)
            sentence_texts = [s['text'] for s in sentences_with_source]
            sentence_embeddings = embedding_generator.embed_batch(sentence_texts)
            
        except Exception as e:
            logger.error(f"Embedding failed during summarization: {e}")
            # Fallback: return first few sentences
            return ' '.join([s['text'] for s in sentences_with_source[:max_sentences]])
        
        # Rank sentences by relevance to query
        scores = cosine_similarity(
            sentence_embeddings,
            query_embedding.reshape(1, -1)
        ).flatten()
        
        # Select diverse, relevant sentences
        selected_indices = self._select_diverse_sentences(
            scores,
            sentence_embeddings,
            max_sentences
        )
        
        # Sort by original document order for coherence
        selected_indices = sorted(
            selected_indices,
            key=lambda i: (
                sentences_with_source[i]['chunk_idx'],
                sentences_with_source[i]['sent_idx']
            )
        )
        
        # Combine selected sentences
        summary_sentences = [sentences_with_source[i]['text'] for i in selected_indices]
        summary = ' '.join(summary_sentences)
        
        logger.debug(
            f"Generated summary with {len(summary_sentences)} sentences "
            f"from {len(sentences_with_source)} candidates"
        )
        
        return summary
    
    def _extract_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentences = self.sentence_pattern.split(text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _select_diverse_sentences(
        self,
        scores: np.ndarray,
        embeddings: np.ndarray,
        max_sentences: int
    ) -> List[int]:
        """
        Select top sentences while maintaining diversity (MMR-like approach).
        
        Args:
            scores: Relevance scores for each sentence
            embeddings: Sentence embeddings
            max_sentences: Number of sentences to select
            
        Returns:
            Indices of selected sentences
        """
        selected = []
        remaining = list(range(len(scores)))
        
        # Always select highest scoring sentence
        best_idx = int(np.argmax(scores))
        selected.append(best_idx)
        remaining.remove(best_idx)
        
        # Iteratively select sentences that are relevant but diverse
        while len(selected) < max_sentences and remaining:
            best_score = -1
            best_idx = None
            
            for idx in remaining:
                # Relevance to query
                relevance = scores[idx]
                
                # Diversity: similarity to already selected sentences
                selected_embeddings = embeddings[selected]
                similarities = cosine_similarity(
                    embeddings[idx].reshape(1, -1),
                    selected_embeddings
                ).flatten()
                max_similarity = np.max(similarities)
                
                # Skip if too similar to existing selections
                if max_similarity > self.diversity_threshold:
                    continue
                
                # Combined score (could tune weights)
                combined_score = relevance - 0.3 * max_similarity
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_idx = idx
            
            if best_idx is not None:
                selected.append(best_idx)
                remaining.remove(best_idx)
            else:
                # No diverse sentences left, take highest scoring
                if remaining:
                    best_idx = max(remaining, key=lambda i: scores[i])
                    selected.append(best_idx)
                    remaining.remove(best_idx)
        
        return selected


# Global instance
extractive_summarizer = ExtractiveSummarizer(
    max_sentences=settings.summary_max_sentences
)
