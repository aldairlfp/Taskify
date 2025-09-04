from sqlmodel import create_engine, SQLModel, Session
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://username:password@localhost:5432/taskify_db"
)

# Create SQLModel engine
engine = create_engine(DATABASE_URL, echo=True)  # echo=True for debugging


# Dependency to get database session
def get_db():
    """
    Creates a database session and ensures it's closed after use.
    This will be used as a dependency in our FastAPI endpoints.
    """
    with Session(engine) as session:
        yield session
