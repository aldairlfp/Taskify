from sqlmodel import SQLModel
from app.core.database import engine
from app.models.models import User, Task


def create_tables():
    """
    Create all tables in the database.
    This function will create the tables based on our SQLModel models.
    """
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully!")


def drop_tables():
    """
    Drop all tables in the database.
    Use with caution - this will delete all data!
    """
    print("Dropping database tables...")
    SQLModel.metadata.drop_all(engine)
    print("Database tables dropped!")


if __name__ == "__main__":
    # This will run when you execute: python -m app.core.init_db
    create_tables()
