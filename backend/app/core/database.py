from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings

# Async engine for FastAPI
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Sync engine for migrations and operations that need sync
sync_engine = create_engine(
    settings.database_sync_url,
    echo=settings.debug,
    future=True
)

SessionLocal = sessionmaker(
    sync_engine,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_sync_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
