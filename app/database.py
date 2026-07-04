import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Define where the local database file will be saved
DATABASE_URL = "sqlite:///./data/evaluation_agent.db"

# Automatically create a 'data' folder if it doesn't exist yet
os.makedirs("./data", exist_ok=True)

# Create the SQLite database engine connection
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Essential setting for SQLite with FastAPI
)

# Create a session factory for managing requests
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency function to handle opening and closing database connections cleanly
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()