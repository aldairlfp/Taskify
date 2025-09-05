from sqlmodel import create_engine, SQLModel, Session
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://username:password@localhost:5432/taskify_db"
)

# Create SQLModel engine with production-optimized settings
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Disable SQL logging in production
    pool_size=10,  # Connection pool size for concurrency
    max_overflow=20,  # Additional connections when pool is full
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections after 1 hour
)


# Dependency to get database session
def get_db():
    """
    Creates a database session and ensures it's closed after use.
    This will be used as a dependency in our FastAPI endpoints.
    """
    with Session(engine) as session:
        yield session
