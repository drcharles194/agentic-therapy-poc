"""
User management endpoints for the Collaborative PoC.

Provides RESTful endpoints for user creation, retrieval, and therapy data analysis.
"""
import logging
import uuid
import time
import asyncio
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from backend.models.schema import (
    User, 
    CreateUserRequest, 
    UpdateUserRequest, 
    UserListResponse,
    TherapistQueryRequest,
    TherapistQueryResponse,
    GraphRAGComparisonResponse,
    GraphRAGComparisonResult,
    ErrorResponse
)
from backend.services.neo4j import Neo4jService, get_neo4j_service
from backend.services.anthropic_service import anthropic_service
from backend.services.graphrag import Neo4jGraphRAGService
from backend.services.official_graphrag import OfficialGraphRAGService
from backend.utils.name_generator import generate_unique_name

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/users", tags=["users"])


def get_graphrag_service(
    neo4j_service: Neo4jService = Depends(get_neo4j_service)
) -> Neo4jGraphRAGService:
    """Dependency to get GraphRAG service instance."""
    return Neo4jGraphRAGService(neo4j_service)


def get_official_graphrag_service(
    neo4j_service: Neo4jService = Depends(get_neo4j_service)
) -> OfficialGraphRAGService:
    """Dependency to get Official GraphRAG service instance."""
    return OfficialGraphRAGService(neo4j_service)


@router.post("/", response_model=User)
async def create_user(
    request: CreateUserRequest,
    neo4j_service: Neo4jService = Depends(get_neo4j_service)
) -> User:
    """
    Create a new user with UUID and friendly name.
    
    Args:
        request: User creation request with optional custom name
        neo4j_service: Neo4j service dependency
        
    Returns:
        User: The created user with UUID and friendly name
    """
    try:
        # Generate unique UUID for user_id
        user_id = str(uuid.uuid4())
        
        # Use provided name or generate a friendly one
        if request.name:
            # Validate name isn't already taken
            existing_users = await neo4j_service.get_all_users()
            existing_names = [user["name"] for user in existing_users if user.get("name")]
            
            if request.name.lower() in [name.lower() for name in existing_names]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Name '{request.name}' is already taken. Please choose a different name."
                )
            user_name = request.name
        else:
            # Generate unique friendly name
            existing_users = await neo4j_service.get_all_users()
            existing_names = [user["name"] for user in existing_users if user.get("name")]
            user_name = generate_unique_name(existing_names)
        
        # Create user in Neo4j
        success = await neo4j_service._ensure_user_exists(user_id, user_name)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to create user in database"
            )
        
        logger.info(f"Created new user: {user_id} ({user_name})")
        
        return User(
            user_id=user_id,
            name=user_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while creating user"
        )


@router.get("/", response_model=UserListResponse)
async def list_users(
    neo4j_service: Neo4jService = Depends(get_neo4j_service)
) -> UserListResponse:
    """
    Get list of all users with conversation data.
    
    Args:
        neo4j_service: Neo4j service dependency
        
    Returns:
        UserListResponse: List of users with metadata
    """
    try:
        users_data = await neo4j_service.get_all_users()
        
        users = []
        for user_data in users_data:
            user = User(
                user_id=user_data["user_id"],
                name=user_data.get("name", user_data["user_id"][-8:]),  # Fallback to last 8 chars if no name
                created_at=user_data.get("created_at"),
                last_active=user_data.get("last_active"),
                moment_count=user_data.get("moment_count", 0)
            )
            users.append(user)
        
        # Sort by last activity (most recent first)
        users.sort(key=lambda u: u.last_active, reverse=True)
        
        logger.info(f"Retrieved {len(users)} users")
        return UserListResponse(users=users)
        
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving users"
        )


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    neo4j_service: Neo4jService = Depends(get_neo4j_service)
) -> User:
    """
    Get a specific user by ID.
    
    Args:
        user_id: The user's UUID
        neo4j_service: Neo4j service dependency
        
    Returns:
        User: The requested user
    """
    try:
        users_data = await neo4j_service.get_all_users()
        user_data = next((u for u in users_data if u["user_id"] == user_id), None)
        
        if not user_data:
            raise HTTPException(
                status_code=404,
                detail=f"User {user_id} not found"
            )
        
        return User(
            user_id=user_data["user_id"],
            name=user_data.get("name", user_data["user_id"][-8:]),
            created_at=user_data.get("created_at"),
            last_active=user_data.get("last_active"),
            moment_count=user_data.get("moment_count", 0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving user"
        )


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    neo4j_service: Neo4jService = Depends(get_neo4j_service)
) -> User:
    """
    Update a user's information (currently just name).
    
    Args:
        user_id: The user's UUID
        request: Update request with new name
        neo4j_service: Neo4j service dependency
        
    Returns:
        User: The updated user
    """
    try:
        # Check if user exists
        users_data = await neo4j_service.get_all_users()
        user_data = next((u for u in users_data if u["user_id"] == user_id), None)
        
        if not user_data:
            raise HTTPException(
                status_code=404,
                detail=f"User {user_id} not found"
            )
        
        # Check if new name is already taken by another user
        existing_names = [u["name"] for u in users_data if u.get("name") and u["user_id"] != user_id]
        if request.name.lower() in [name.lower() for name in existing_names]:
            raise HTTPException(
                status_code=400,
                detail=f"Name '{request.name}' is already taken. Please choose a different name."
            )
        
        # Update user name in Neo4j
        success = await neo4j_service.update_user_name(user_id, request.name)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to update user in database"
            )
        
        logger.info(f"Updated user {user_id} name to: {request.name}")
        
        return User(
            user_id=user_id,
            name=request.name,
            created_at=user_data.get("created_at"),
            last_active=user_data.get("last_active"),
            moment_count=user_data.get("moment_count", 0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while updating user"
        )


@router.post("/{user_id}/query", response_model=TherapistQueryResponse)
async def query_user_data(
    user_id: str,
    request: TherapistQueryRequest,
    graphrag_service: Neo4jGraphRAGService = Depends(get_graphrag_service)
) -> TherapistQueryResponse:
    """
    Execute a GraphRAG query to analyze user data for therapists.
    
    This endpoint allows therapists to ask natural language questions about a user's
    therapy data and receive intelligent insights based on the user's conversation history,
    emotions, reflections, patterns, and other stored information.
    
    Args:
        user_id: The user's UUID to query data for
        request: TherapistQueryRequest with the natural language query
        graphrag_service: GraphRAG service dependency
        
    Returns:
        TherapistQueryResponse: Natural language analysis with insights and data sources
    """
    logger.info(f"Therapist query for user {user_id}: {request.query[:100]}...")
    
    try:
        # Execute GraphRAG query
        result = await graphrag_service.query_user_data(
            user_id=user_id,
            query=request.query,
            context=request.context
        )
        
        # Convert GraphRAG result to API response
        response = TherapistQueryResponse(
            query=result.query,
            user_id=result.user_id,
            user_name=result.user_name,
            response=result.natural_response,
            confidence=result.confidence,
            data_sources=result.data_sources
        )
        
        logger.info(f"Completed GraphRAG query for user {user_id} with confidence {result.confidence:.2f}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing GraphRAG query for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing query"
        )


@router.post("/{user_id}/query/compare", response_model=GraphRAGComparisonResponse)
async def compare_graphrag_implementations(
    user_id: str,
    request: TherapistQueryRequest,
    custom_graphrag: Neo4jGraphRAGService = Depends(get_graphrag_service),
    official_graphrag: OfficialGraphRAGService = Depends(get_official_graphrag_service)
) -> GraphRAGComparisonResponse:
    """
    Execute concurrent GraphRAG queries to compare custom vs official implementations.
    
    This endpoint runs both the custom optimized GraphRAG and the official Neo4j GraphRAG
    implementations simultaneously to provide a side-by-side comparison of approaches,
    performance, and results.
    
    Args:
        user_id: The user's UUID to query data for
        request: TherapistQueryRequest with the natural language query
        custom_graphrag: Custom GraphRAG service dependency
        official_graphrag: Official Neo4j GraphRAG service dependency
        
    Returns:
        GraphRAGComparisonResponse: Comparison results from both implementations
    """
    logger.info(f"GraphRAG comparison query for user {user_id}: {request.query[:100]}...")
    
    try:
        start_time = time.time()
        
        # Run both GraphRAG implementations concurrently
        custom_start = time.time()
        official_start = time.time()
        
        # Execute both queries in parallel using asyncio.gather
        custom_task = custom_graphrag.query_user_data(
            user_id=user_id,
            query=request.query,
            context=request.context
        )
        
        official_task = official_graphrag.query_user_data(
            user_id=user_id,
            query=request.query,
            context=request.context
        )
        
        # Wait for both to complete
        custom_result, official_result = await asyncio.gather(
            custom_task, official_task, return_exceptions=True
        )
        
        custom_end = time.time()
        official_end = time.time()
        
        # Handle any exceptions from the tasks
        if isinstance(custom_result, Exception):
            logger.error(f"Custom GraphRAG failed: {custom_result}")
            custom_comparison_result = GraphRAGComparisonResult(
                implementation="Custom (Multi-Index)",
                response=f"Error: {str(custom_result)}",
                confidence=0.0,
                data_sources=[],
                processing_time_ms=(custom_end - custom_start) * 1000,
                indexes_used=[],
                retrieval_method="direct_vector_search",
                error=str(custom_result)
            )
        else:
            # Extract information from custom result
            custom_comparison_result = GraphRAGComparisonResult(
                implementation="Custom (Multi-Index)",
                response=custom_result.natural_response,
                confidence=custom_result.confidence,
                data_sources=custom_result.data_sources,
                processing_time_ms=(custom_end - custom_start) * 1000,
                indexes_used=custom_result.data_sources,  # Custom uses data_sources as index info
                retrieval_method="direct_vector_search"
            )
        
        if isinstance(official_result, Exception):
            logger.error(f"Official GraphRAG failed: {official_result}")
            official_comparison_result = GraphRAGComparisonResult(
                implementation="Official Neo4j GraphRAG",
                response=f"Error: {str(official_result)}",
                confidence=0.0,
                data_sources=[],
                processing_time_ms=(official_end - official_start) * 1000,
                indexes_used=[],
                retrieval_method="official_multi_index_retrieval",
                error=str(official_result)
            )
        else:
            # Extract information from official result
            official_comparison_result = GraphRAGComparisonResult(
                implementation="Official Neo4j GraphRAG",
                response=official_result.natural_response,
                confidence=official_result.confidence,
                data_sources=official_result.data_sources,
                processing_time_ms=(official_end - official_start) * 1000,
                indexes_used=official_result.data_sources,  # Official uses data_sources as retriever info
                retrieval_method=official_result.retrieval_method
            )
        
        total_time = (time.time() - start_time) * 1000
        
        # Get user name for response
        user_name = "Unknown"
        if not isinstance(custom_result, Exception):
            user_name = custom_result.user_name
        elif not isinstance(official_result, Exception):
            user_name = official_result.user_name
        
        # Create comparison response
        comparison_response = GraphRAGComparisonResponse(
            query=request.query,
            user_id=user_id,
            user_name=user_name,
            custom_result=custom_comparison_result,
            official_result=official_comparison_result,
            total_processing_time_ms=total_time
        )
        
        logger.info(f"Completed GraphRAG comparison for user {user_id} in {total_time:.2f}ms")
        return comparison_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing GraphRAG comparison for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing comparison query"
        ) 