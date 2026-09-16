from pydantic import BaseModel, validator, ValidationError
from typing import Optional
import os
import re


class AppConfigValidation(BaseModel):
    """Validate application configuration on startup"""
    
    # Required fields
    llm_endpoint: str
    llm_api_key: str
    database_url: str
    database_sync_url: str
    secret_key: str
    
    # Optional fields with defaults
    llm_model: str = "gpt2"
    llm_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    app_name: str = "CortexDesk"
    debug: bool = False
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        """Validate that secret key is not the default placeholder"""
        if v == "your-secret-key-change-this-in-production":
            raise ValueError(
                "SECRET_KEY must be changed from the default value. "
                "Please set a secure random string in your .env file."
            )
        if len(v) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters long for security."
            )
        return v
    
    @validator('llm_endpoint')
    def validate_llm_endpoint(cls, v):
        """Validate LLM endpoint configuration"""
        if v == "local":
            return v
        if not v.startswith(("http://", "https://")):
            raise ValueError(
                "LLM_ENDPOINT must be 'local' or a valid HTTP/HTTPS URL."
            )
        return v
    
    @validator('database_url', 'database_sync_url')
    def validate_database_url(cls, v):
        """Validate database URL format"""
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError(
                "DATABASE_URL must be a valid PostgreSQL connection string."
            )
        return v
    
    @validator('redis_url')
    def validate_redis_url(cls, v):
        """Validate Redis URL format"""
        if not v.startswith("redis://"):
            raise ValueError("REDIS_URL must be a valid Redis connection string.")
        return v
    
    @validator('qdrant_url')
    def validate_qdrant_url(cls, v):
        """Validate Qdrant URL format"""
        if not v.startswith(("http://", "https://")):
            raise ValueError("QDRANT_URL must be a valid HTTP/HTTPS URL.")
        return v


def validate_config() -> dict:
    """
    Validate application configuration on startup.
    Returns validation result with status and errors if any.
    """
    from app.core.config import settings
    
    try:
        config = AppConfigValidation(
            llm_endpoint=settings.llm_endpoint,
            llm_api_key=settings.llm_api_key,
            database_url=settings.database_url,
            database_sync_url=settings.database_sync_url,
            secret_key=settings.secret_key,
            llm_model=settings.llm_model,
            llm_embedding_model=settings.llm_embedding_model,
            redis_url=settings.redis_url,
            qdrant_url=settings.qdrant_url,
            app_name=settings.app_name,
            debug=settings.debug
        )
        return {
            "status": "valid",
            "config": config.dict(),
            "errors": []
        }
    except ValidationError as e:
        return {
            "status": "invalid",
            "config": None,
            "errors": [
            {
                "field": error["loc"][0] if error["loc"] else "unknown",
                "message": error["msg"]
            }
            for error in e.errors()
        ]
        }
    except Exception as e:
        return {
            "status": "error",
            "config": None,
            "errors": [{"field": "system", "message": str(e)}]
        }


class APIError(Exception):
    """Custom API error with status code and detail"""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class ServiceUnavailableError(APIError):
    """Service unavailable error"""
    def __init__(self, service_name: str):
        super().__init__(
            status_code=503,
            detail=f"{service_name} service is currently unavailable"
        )


class ConfigurationError(APIError):
    """Configuration error"""
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail)


class ValidationError(APIError):
    """Validation error"""
    def __init__(self, detail: str):
        super().__init__(status_code=422, detail=detail)