"""Database configuration and utilities."""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import os

# Connection string — SQLite for MVP, PostgreSQL for production
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./cloudops_ai.db"  # Local file-based SQLite
)

# Create engine (no connection pooling for simplicity in MVP)
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=False  # Set to True for SQL debugging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for ORM models
Base = declarative_base()

def get_db():
    """Dependency for FastAPI to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database (create tables if not exist)."""
    # Import models to register them with Base
    from cloudops_ai.models import orm  # noqa: F401
    Base.metadata.create_all(bind=engine)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign keys and set pragmas for SQLite."""
    if DATABASE_URL.startswith("sqlite:"):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    else:
        # PostgreSQL — set timezone
        cursor = dbapi_conn.cursor()
        cursor.execute("SET timezone TO 'UTC'")
        cursor.close()
