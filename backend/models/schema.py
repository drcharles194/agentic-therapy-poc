"""
Shared Pydantic models for API request and response schemas.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from uuid import uuid4


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    user_id: str = Field(..., description="Unique identifier for the user")
    message: str = Field(..., min_length=1, description="User's message to send to the persona")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    persona_response: str = Field(..., description="Response from the active persona")


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(default="healthy", description="Service health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    version: str = Field(..., description="Application version")
    services: Dict[str, str] = Field(default_factory=dict, description="Status of dependent services")


class PersonaNote(BaseModel):
    """Model for persona-specific notes attached to reflections."""
    persona: str = Field(..., description="Name of the persona that created this note")
    type: str = Field(..., description="Type of note (e.g., gentle_reframe, observation)")
    content: str = Field(..., description="Content of the persona note")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the note was created")
    user_id: str = Field(..., description="User this note belongs to")


class Reflection(BaseModel):
    """Model for user reflections stored in memory."""
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the reflection was created")
    archived: bool = Field(default=False, description="Whether this reflection is archived")
    source: str = Field(..., description="Source of the reflection (user, agent, etc.)")
    agent_origin: Optional[str] = Field(None, description="Which agent created this reflection")
    user_id: str = Field(..., description="User this reflection belongs to")
    content: str = Field(..., description="The reflection content")
    persona_notes: List[PersonaNote] = Field(default_factory=list, description="Notes from various personas")


class Emotion(BaseModel):
    """Model for emotions tracked in memory."""
    label: str = Field(..., description="Emotion label (e.g., sadness, joy)")
    intensity: float = Field(..., ge=0.0, le=1.0, description="Emotion intensity from 0 to 1")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the emotion was recorded")
    archived_at: Optional[datetime] = Field(None, description="When the emotion was archived")
    user_id: str = Field(..., description="User this emotion belongs to")


class SelfKindnessEvent(BaseModel):
    """Model for self-kindness events tracked in memory."""
    description: str = Field(..., description="Description of the self-kindness event")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the event occurred")
    user_id: str = Field(..., description="User this event belongs to")


class Contradiction(BaseModel):
    """Model for contradictions or tensions identified in user's values/behavior."""
    summary: str = Field(..., description="Summary of the contradiction")
    user_id: str = Field(..., description="User this contradiction belongs to")


class UserMemory(BaseModel):
    """Complete memory context for a user."""
    user_id: str = Field(..., description="User identifier")
    user_name: Optional[str] = Field(None, description="User's display name")
    sage: Dict[str, Any] = Field(default_factory=dict, description="Sage persona-specific memory data")


class ErrorResponse(BaseModel):
    """RFC 7807 compliant error response model."""
    type: str = Field(..., description="Error type URI")
    title: str = Field(..., description="Short, human-readable summary")
    status: int = Field(..., description="HTTP status code")
    detail: str = Field(..., description="Human-readable explanation")
    instance: str = Field(..., description="URI reference to the specific occurrence") 