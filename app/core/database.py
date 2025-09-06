from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from environment variables - Convert to async format
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://username:password@localhost:5432/taskify_db"
)

# Convert postgresql:// to postgresql+asyncpg:// for async support
if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# Create async SQLModel engine with high-concurrency optimized settings
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,  # Disable SQL logging in production
    pool_size=20,  # Increased base connection pool for high concurrency
    max_overflow=30,  # Additional connections when pool is full (total: 50)
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=1800,  # Recycle connections after 30 minutes (faster refresh)
    # Async specific settings optimized for concurrency
    pool_timeout=10,  # Reduced timeout for faster fail-over
    connect_args={
        "command_timeout": 30,  # Reduced command timeout
        "server_settings": {
            "jit": "off",  # Disable JIT for better performance in some cases
        },
    },
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Async dependency to get database session
async def get_db():
    """
    Creates an async database session and ensures it's closed after use.
    This will be used as a dependency in our FastAPI endpoints.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Function to create tables (for initialization)
async def create_tables():
    """
    Create all database tables asynchronously.
    This should be called during application startup.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# Function to close the engine (for cleanup)
async def close_async_engine():
    """
    Close the async engine and all connections.
    This should be called during application shutdown.
    """
    await async_engine.dispose()
