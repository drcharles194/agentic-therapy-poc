"""
Chat router for handling user interactions with personas.
"""
import logging
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from backend.models.schema import ChatRequest, ChatResponse, UserMemory, HealthCheckResponse
from backend.services.router import persona_router
from backend.services.neo4j import neo4j_service
from backend.services.anthropic_service import anthropic_service
from backend.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat/", response_model=ChatResponse)
async def chat_with_persona(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint for interacting with personas.
    
    This endpoint will:
    1. Route the message to the appropriate persona (Sage for now)
    2. Inject relevant memory context from Neo4j
    3. Generate a response using LangChain + Claude
    4. Optionally propose memory updates
    """
    logger.info(f"Chat request from user {request.user_id}: {request.message[:50]}...")
    
    try:
        # Route message through the persona router system
        persona_response = await persona_router.route_message(
            user_id=request.user_id,
            message=request.message
        )
        
        response = ChatResponse(persona_response=persona_response)
        logger.info(f"Generated response for user {request.user_id}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat request for user {request.user_id}: {e}")
        # Return fallback response
        fallback_response = ChatResponse(
            persona_response="I'm here with you. Something went wrong on my end, but I'm listening."
        )
        return fallback_response


@router.get("/memory/{user_id}", response_model=UserMemory)
async def get_user_memory(user_id: str) -> UserMemory:
    """
    Retrieve user memory context from Neo4j.
    
    Returns structured memory including:
    - Reflections with persona notes
    - Emotions and their intensities
    - Self-kindness events
    - Contradictions/tensions
    """
    logger.info(f"Memory request for user {user_id}")
    
    try:
        # Use Neo4j service for real memory retrieval
        memory_data = await neo4j_service.get_user_memory_for_display(user_id)
        
        # Convert to UserMemory format
        user_memory = UserMemory(
            user_id=memory_data["user_id"],
            user_name=memory_data["user_name"],
            sage=memory_data["sage"]
        )
        
        logger.info(f"Retrieved memory for user {user_id}")
        return user_memory
        
    except Exception as e:
        logger.error(f"Error retrieving memory for user {user_id}: {e}")
        # Return fallback mock memory data
        mock_memory = UserMemory(
            user_id=user_id,
            user_name="Jon Smith",
            sage={
                "reflections": [
                    {
                        "timestamp": "2024-06-01T10:32:00Z",
                        "id": "uuid1",
                        "archived": False,
                        "source": "user",
                        "agent_origin": None,
                        "user_id": user_id,
                        "content": "I feel like I've been running without direction.",
                        "persona_notes": [
                            {
                                "persona": "Sage",
                                "type": "gentle_reframe",
                                "content": "This reflection carries ambivalence. Would you like to revisit this later?",
                                "created_at": "2024-06-02T16:45:00Z",
                                "user_id": user_id
                            }
                        ]
                    }
                ],
                "emotions": [
                    {
                        "label": "sadness",
                        "intensity": 0.7,
                        "timestamp": "2024-05-20T09:00:00Z",
                        "archived_at": None,
                        "user_id": user_id
                    }
                ],
                "self_kindness_events": [
                    {
                        "description": "Took a walk instead of spiraling",
                        "timestamp": "2024-06-01T14:00:00Z",
                        "user_id": user_id
                    }
                ],
                "contradictions": [
                    {
                        "summary": "Wants to feel free, but avoids taking space",
                        "user_id": user_id
                    }
                ]
            }
        )
        
        logger.info(f"Retrieved fallback memory for user {user_id}")
        return mock_memory


@router.post("/healthcheck", response_model=HealthCheckResponse)
async def healthcheck() -> HealthCheckResponse:
    """Basic health check endpoint for system readiness and availability."""
    logger.info("Health check requested")
    
    # Check service health
    services = {}
    
    # Neo4j health check
    try:
        neo4j_health = await neo4j_service.health_check()
        services["neo4j"] = neo4j_health["status"]
    except Exception as e:
        logger.error(f"Neo4j health check failed: {e}")
        services["neo4j"] = "error"
    
    # Anthropic health check
    try:
        anthropic_health = await anthropic_service.health_check()
        services["anthropic"] = anthropic_health["status"]
    except Exception as e:
        logger.error(f"Anthropic health check failed: {e}")
        services["anthropic"] = "error"
    
    response = HealthCheckResponse(
        version=settings.app_version,
        services=services
    )
    
    logger.info(f"Health check completed: {services}")
    return response 