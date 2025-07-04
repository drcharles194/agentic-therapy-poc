"""
Configuration settings for the Collaborative backend.
"""
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_reload: bool = Field(default=True, env="API_RELOAD")
    
    # Application metadata
    app_name: str = Field(default="Collaborative PoC", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    debug: bool = Field(default=True, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Neo4j Configuration
    neo4j_uri: str = Field(default="bolt://localhost:7687", env="NEO4J_URI")
    neo4j_username: str = Field(default="neo4j", env="NEO4J_USERNAME")
    neo4j_password: str = Field(default="test_password", env="NEO4J_PASSWORD")
    neo4j_database: str = Field(default="neo4j", env="NEO4J_DATABASE")
    
    # Anthropic/Claude Configuration
    anthropic_api_key: str = Field(default="test_key", env="ANTHROPIC_API_KEY")
    
    # CORS Settings
    allowed_origins: List[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        env="ALLOWED_ORIGINS"
    )
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }


# Global settings instance
settings = Settings()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent 