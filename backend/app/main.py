from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import async_engine, Base, get_async_db
from app.core.redis import redis_manager
from app.core.qdrant import qdrant_manager
from app.core.validation import validate_config, ConfigurationError
from app.api.main import router as api_router
from app.api.observability import router as observability_router
from app.api.screenshot import router as screenshot_router
from app.api.terminal import router as terminal_router
from app.api.documents import router as documents_router
from app.api.mcp import router as mcp_router
from app.api.llm_config import router as llm_config_router
from app.services.observability import logger, performance_monitor, error_tracker
from app.models.chat import Chat, Message
from app.models.user import User
from app.models.memory import Memory, AgentExecution, LLMConfiguration, LLMProvider
from app.models.document import Document
from app.models.mcp import MCPIntegration
from sqlalchemy import select


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    logger.info(f"Starting {settings.app_name} backend...")
    
    # Validate configuration
    config_validation = validate_config()
    if config_validation["status"] != "valid":
        logger.error(f"Configuration validation failed: {config_validation['errors']}")
        raise ConfigurationError(
            f"Invalid configuration: {', '.join([e['message'] for e in config_validation['errors']])}"
        )
    logger.info("Configuration validation passed")
    
    # Create database tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")
    
    # Initialize default LLM configurations for all users
    async for db in get_async_db():
        # Get all users
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        for user in users:
            # Check if user has any LLM configuration
            config_result = await db.execute(
                select(LLMConfiguration)
                .where(LLMConfiguration.user_id == user.id)
            )
            configs = config_result.scalars().all()
            
            # If no configuration exists, create default local configuration
            if len(configs) == 0:
                default_config = LLMConfiguration(
                    user_id=user.id,
                    provider=LLMProvider.LOCAL,
                    model_name="gpt2",
                    endpoint=None,
                    api_key=None,
                    temperature=0.7,
                    max_tokens=1000,
                    is_active=True
                )
                db.add(default_config)
                await db.commit()
                logger.info(f"Created default LLM configuration for user {user.id}")
        
        logger.info("Default LLM configurations initialized")
    
    # Connect to Redis
    await redis_manager.connect()
    logger.info("Connected to Redis")
    
    # Connect to Qdrant and create collection
    qdrant_manager.connect()
    await qdrant_manager.create_collection(settings.qdrant_collection_name, vector_size=384)
    logger.info("Connected to Qdrant")
    
    # Start performance monitoring
    import asyncio
    asyncio.create_task(performance_monitor_task())
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.app_name} backend...")
    await redis_manager.disconnect()
    logger.info("Disconnected from Redis")


async def performance_monitor_task():
    """Background task to monitor system performance"""
    import asyncio
    while True:
        try:
            await performance_monitor.track_memory_usage()
            await performance_monitor.track_cpu_usage()
            await asyncio.sleep(60)  # Monitor every minute
        except Exception as e:
            logger.error(f"Performance monitoring error: {str(e)}")
            await asyncio.sleep(60)


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Multi-agent Windows AI Assistant backend",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(observability_router, prefix="/api/v1")
app.include_router(screenshot_router, prefix="/api/v1")
app.include_router(terminal_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(mcp_router, prefix="/api/v1")
app.include_router(llm_config_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"{settings.app_name} API",
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    config_validation = validate_config()
    return {
        "status": "healthy" if config_validation["status"] == "valid" else "unhealthy",
        "version": settings.app_version,
        "configuration": config_validation["status"],
        "services": {
            "api": "running",
            "redis": "connected" if redis_manager.redis else "disconnected",
            "qdrant": "connected" if qdrant_manager.client else "disconnected"
        }
    }


@app.get("/config")
async def config_check():
    """Configuration check endpoint"""
    return validate_config()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
