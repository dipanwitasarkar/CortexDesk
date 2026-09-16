from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Dell LLM Configuration
    dell_llm_endpoint: str
    dell_llm_api_key: str
    dell_llm_model: str = "gpt-4"
    dell_llm_embedding_model: str = "text-embedding-ada-002"

    # Database Configuration
    database_url: str
    database_sync_url: str

    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 3600

    # Qdrant Configuration
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection_name: str = "ai_assistant_memory"

    # Application Configuration
    app_name: str = "Windows AI Assistant"
    app_version: str = "1.0.0"
    debug: bool = True
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS Configuration
    frontend_url: str = "http://localhost:3000"
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    # File Upload Configuration
    max_upload_size: int = 10485760  # 10MB
    upload_dir: str = "./uploads"

    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"

    # MCP Configuration
    mcp_server_timeout: int = 30
    mcp_max_retries: int = 3

    # Agent Configuration
    agent_timeout: int = 120
    max_concurrent_agents: int = 5

    # RAG Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]


settings = Settings()
