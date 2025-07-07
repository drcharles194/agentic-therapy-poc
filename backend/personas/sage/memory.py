"""
Memory access layer for the Sage persona.

Provides read and write methods for Sage-specific memory operations,
including user context retrieval and memory update proposals.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.services.neo4j import neo4j_service

logger = logging.getLogger(__name__)


async def get_user_context(user_id: str) -> Dict[str, Any]:
    """
    Retrieve user memory context relevant to the Sage persona.
    
    This is the main read method for Sage memory access.
    
    Args:
        user_id: Unique identifier for the user
        
    Returns:
        Dict containing user context with sage-specific memory data
    """
    logger.info(f"Retrieving Sage memory context for user {user_id}")
    
    try:
        # Use Neo4j service for real memory retrieval
        user_context = await neo4j_service.get_user_memory(user_id)
        
        logger.info(f"Retrieved memory context for user {user_id}")
        return user_context
        
    except Exception as e:
        logger.error(f"Error retrieving memory context for user {user_id}: {e}")
        # Return minimal context on error with fallback to mock data
        return _get_fallback_context(user_id)


def _get_fallback_context(user_id: str) -> Dict[str, Any]:
    """Generate minimal fallback context when Neo4j is unavailable."""
    logger.warning(f"Using fallback context for user {user_id}")
    
    return {
        "user_id": user_id,
        "user_name": "Demo User",
        "sage": {
            "moments": [],
            "emotions": [],
            "reflections": [],
            "values": [],
            "patterns": [],
            "contradictions": [],
            "recent_persona_notes": []
        }
    }

 