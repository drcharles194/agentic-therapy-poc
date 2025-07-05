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
    """Generate fallback context when Neo4j is unavailable."""
    logger.warning(f"Using fallback context for user {user_id}")
    
    return {
        "user_id": user_id,
        "user_name": "Demo User",
        "sage": {
            "moments": [
                {
                    "moment": {
                        "id": "demo-moment-1",
                        "timestamp": "2024-06-01T10:32:00Z",
                        "context": "Feeling uncertain about direction in life"
                    },
                    "emotions": [
                        {
                            "emotion": {
                                "id": "demo-emotion-1",
                                "label": "anxiety",
                                "intensity": 0.7,
                                "nuance": "anticipatory worry about the future"
                            },
                            "prominence": 0.8
                        }
                    ],
                    "reflections": [
                        {
                            "reflection": {
                                "id": "demo-reflection-1",
                                "content": "I feel like I've been running without direction",
                                "insight_type": "realization",
                                "depth_level": 2,
                                "confidence": 0.8
                            },
                            "spontaneity": 0.6
                        }
                    ]
                }
            ],
            "emotional_patterns": [
                {
                    "emotion": {
                        "id": "demo-emotion-1",
                        "label": "anxiety",
                        "intensity": 0.7,
                        "nuance": "anticipatory worry about the future"
                    },
                    "co_occurs_with": [],
                    "transforms_into": []
                }
            ],
            "reflective_web": [
                {
                    "reflection": {
                        "id": "demo-reflection-1",
                        "content": "I feel like I've been running without direction",
                        "insight_type": "realization",
                        "depth_level": 2,
                        "confidence": 0.8
                    },
                    "builds_on": [],
                    "challenges": [],
                    "inspired_by": [],
                    "explains": []
                }
            ],
            "value_system": [
                {
                    "value": {
                        "id": "demo-value-1",
                        "name": "freedom",
                        "description": "The ability to choose my own path",
                        "importance": 0.9
                    },
                    "strength": 0.8,
                    "awareness": 0.7,
                    "conflicts_with": [
                        {
                            "value": {
                                "name": "security",
                                "description": "Feeling safe and stable"
                            },
                            "context": "when making big life decisions"
                        }
                    ]
                }
            ],
            "patterns": [
                {
                    "pattern": {
                        "id": "demo-pattern-1",
                        "description": "Tends to overthink when facing uncertainty",
                        "pattern_type": "cognitive",
                        "frequency": "frequent"
                    },
                    "emotional_manifestations": [
                        {
                            "emotion": {
                                "label": "anxiety"
                            },
                            "consistency": 0.8
                        }
                    ]
                }
            ],
            "recent_persona_notes": [
                {
                    "id": "demo-note-1",
                    "persona": "Sage",
                    "note_type": "gentle_question",
                    "content": "This reflection carries ambivalence. What feels most important to explore?",
                    "created_at": "2024-06-02T16:45:00Z"
                }
            ]
        }
    }


async def propose_memory_update(
    agent_name: str, 
    user_id: str, 
    update_payload: Dict[str, Any]
) -> bool:
    """
    Propose a memory update for review by the self-governance layer.
    
    This is the write method that enforces Sage-specific memory update rules.
    
    Args:
        agent_name: Name of the agent proposing the update (should be 'Sage')
        user_id: User identifier
        update_payload: Dictionary containing the proposed changes
        
    Returns:
        bool: True if update was accepted, False otherwise
    """
    logger.info(f"Memory update proposed by {agent_name} for user {user_id}")
    
    # Validate agent permissions
    if agent_name != "Sage":
        logger.warning(f"Agent {agent_name} not authorized for Sage memory updates")
        return False
    
    # Validate update payload structure
    required_fields = ["update_type", "data"]
    if not all(field in update_payload for field in required_fields):
        logger.error(f"Invalid update payload structure: {update_payload.keys()}")
        return False
    
    update_type = update_payload["update_type"]
    data = update_payload["data"]
    
    try:
        # Apply Sage-specific validation rules
        if update_type == "persona_note":
            return await _validate_and_apply_persona_note_update(user_id, data)
        elif update_type == "emotion_observation":
            return await _validate_and_apply_emotion_update(user_id, data)
        elif update_type == "reflection_insight":
            return await _validate_and_apply_reflection_update(user_id, data)
        else:
            logger.warning(f"Unknown update type: {update_type}")
            return False
            
    except Exception as e:
        logger.error(f"Error processing memory update: {e}")
        return False


async def _validate_and_apply_persona_note_update(user_id: str, data: Dict[str, Any]) -> bool:
    """Validate and apply a persona note update according to Sage's rules."""
    
    # Sage can only create gentle, non-directive notes
    allowed_note_types = ["gentle_reframe", "observation", "validation", "curiosity"]
    
    if data.get("type") not in allowed_note_types:
        logger.warning(f"Sage note type {data.get('type')} not allowed")
        return False
    
    # Content should not contain directive language
    content = data.get("content", "").lower()
    directive_phrases = ["you should", "you must", "you need to", "i suggest", "try this"]
    
    if any(phrase in content for phrase in directive_phrases):
        logger.warning("Sage note contains directive language")
        return False
    
    # Apply the update via Neo4j service
    try:
        reflection_id = data.get("reflection_id")
        if not reflection_id:
            logger.error("No reflection_id provided for persona note")
            return False
        
        success = await neo4j_service.add_persona_note(user_id, reflection_id, {
            "persona": "Sage",
            "type": data.get("type"),
            "content": data.get("content")
        })
        
        if success:
            logger.info(f"Persona note update applied for user {user_id}")
            return True
        else:
            logger.error(f"Failed to apply persona note update for user {user_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error applying persona note update: {e}")
        return False


async def _validate_and_apply_emotion_update(user_id: str, data: Dict[str, Any]) -> bool:
    """Validate and apply an emotion observation update."""
    
    # Sage can observe emotions but not override user's own emotional experience
    if data.get("source") != "sage_observation":
        logger.warning("Sage can only add emotion observations, not primary emotions")
        return False
    
    # TODO: Implement emotion update in Neo4j
    logger.info(f"Emotion update validated for user {user_id} (Neo4j implementation pending)")
    return True


async def _validate_and_apply_reflection_update(user_id: str, data: Dict[str, Any]) -> bool:
    """Validate and apply a reflection insight update."""
    
    # Sage can add insights but cannot modify user's original reflections
    if data.get("modification_type") == "edit_original":
        logger.warning("Sage cannot modify original user reflections")
        return False
    
    # TODO: Implement reflection update in Neo4j
    logger.info(f"Reflection update validated for user {user_id} (Neo4j implementation pending)")
    return True 