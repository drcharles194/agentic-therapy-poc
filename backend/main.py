"""
Main FastAPI application for the Collaborative PoC backend.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from backend.config import settings
from backend.models.schema import ErrorResponse
from backend.routers import chat, users
from backend.services.neo4j import neo4j_service
from backend.services.anthropic_service import anthropic_service
from backend.services.official_graphrag import initialize_official_graphrag_service


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Initialize services
    try:
        logger.info("Initializing Neo4j service...")
        await neo4j_service.connect()
        logger.info("Neo4j service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Neo4j service: {e}")
        logger.warning("Neo4j service will fall back to mock responses")
    
    try:
        logger.info("Initializing Anthropic service...")
        # Anthropic service initializes in constructor, just log status
        model_info = anthropic_service.get_model_info()
        logger.info(f"Anthropic service status: {model_info}")
    except Exception as e:
        logger.error(f"Failed to initialize Anthropic service: {e}")
        logger.warning("Anthropic service will fall back to mock responses")
    
    try:
        logger.info("Initializing Official GraphRAG service...")
        initialize_official_graphrag_service(neo4j_service)
        logger.info("Official GraphRAG service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Official GraphRAG service: {e}")
        logger.warning("Official GraphRAG service will fall back to unavailable responses")
    
    yield
    
    # Cleanup services
    logger.info("Shutting down application")
    try:
        await neo4j_service.disconnect()
        logger.info("Neo4j service disconnected")
    except Exception as e:
        logger.error(f"Error disconnecting Neo4j service: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend for Collaborative PoC - An agentic therapy platform with persona-aware LLM orchestration",
    debug=settings.debug,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# RFC 7807 compliant error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with RFC 7807 format."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            type=f"https://collaborative.solutions/errors/{exc.status_code}",
            title=exc.detail,
            status=exc.status_code,
            detail=exc.detail,
            instance=str(request.url)
        ).model_dump()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with RFC 7807 format."""
    error_details = "; ".join([f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors()])
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            type="https://collaborative.solutions/errors/validation-error",
            title="Validation Error",
            status=422,
            detail=f"Request validation failed: {error_details}",
            instance=str(request.url)
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions with RFC 7807 format."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            type="https://collaborative.solutions/errors/internal-error",
            title="Internal Server Error",
            status=500,
            detail="An unexpected error occurred. Please try again later.",
            instance=str(request.url)
        ).model_dump()
    )


# Include routers
app.include_router(chat.router, tags=["chat"])
app.include_router(users.router, tags=["users"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": f"Welcome to {settings.app_name} v{settings.app_version}",
        "docs": "/docs",
        "health": "/healthcheck"
    } 