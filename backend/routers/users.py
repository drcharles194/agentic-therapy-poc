"""
User management API endpoints.
"""
import logging
import uuid
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from backend.models.schema import (
    User, 
    CreateUserRequest, 
    UpdateUserRequest, 
    UserListResponse,
    ErrorResponse
)
from backend.services.neo4j import Neo4jService, get_neo4j_service
from backend.utils.name_generator import generate_unique_name

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/users", tags=["users"])


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