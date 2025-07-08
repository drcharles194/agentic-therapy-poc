"""
Embedding service for generating vector embeddings.

This service provides embedding generation for therapy content
using OpenAI's text-embedding-3-large model.
"""

import logging
from typing import List, Optional
from neo4j_graphrag.embeddings import OpenAIEmbeddings
from backend.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings for therapy content."""
    
    def __init__(self):
        self.embedder: Optional[OpenAIEmbeddings] = None
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the OpenAI embeddings service."""
        if self._initialized:
            return True
            
        try:
            if not settings.openai_api_key or settings.openai_api_key == "test_key":
                logger.warning("OpenAI API key not configured - embeddings will be disabled")
                return False
            
            self.embedder = OpenAIEmbeddings(
                model="text-embedding-3-large",
                api_key=settings.openai_api_key
            )
            self._initialized = True
            logger.info("✅ EmbeddingService initialized with OpenAI text-embedding-3-large")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize EmbeddingService: {e}")
            return False
    
    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a single text string."""
        if not self._initialized or not self.embedder:
            logger.warning("EmbeddingService not initialized - skipping embedding generation")
            return None
            
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding generation")
            return None
            
        try:
            embedding = self.embedder.embed_query(text.strip())
            logger.debug(f"Generated embedding for text: {text[:50]}...")
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding for text '{text[:50]}...': {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if the embedding service is available."""
        return self._initialized and self.embedder is not None


# Global instance
embedding_service = EmbeddingService() 