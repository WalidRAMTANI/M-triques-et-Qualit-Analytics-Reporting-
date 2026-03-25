# app/db.py
"""
SQLAlchemy database configuration and session management.

This module provides:
- Engine creation for SQLite database
- Session factory for database operations
- Database initialization
- Context managers for transaction handling
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from pathlib import Path
from app.database_models import Base

# configure SQLite database location
DATABASE_PATH = Path("platonAAV.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# create database engine with SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

# create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Initialize the database by creating all tables from ORM models.
    
    This function should be called once on application startup to ensure
    all tables defined in the database_models module are created if they
    don't already exist.
    """
    # create all tables in database
    Base.metadata.create_all(bind=engine)
    print("✅ Base de données initialisée")


def get_db() -> Session:
    """
    Get a database session for direct operations.
    
    Returns:
        Session: SQLAlchemy session for database operations.
        
    Raises:
        Exception: If session creation or operations fail.
    """
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e


@contextmanager
def get_db_context():
    """
    Context manager for automatic session management.
    
    Provides automatic commit on success and rollback on error.
    Ensures the session is closed after use.
    
    Yields:
        Session: SQLAlchemy session for use within context.
    """
    db = SessionLocal()
    try:
        yield db
        # commit transaction on success
        db.commit()
    except Exception as e:
        # rollback on error
        db.rollback()
        raise e
    finally:
        db.close()


# enable foreign key constraints in SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Enable SQLite foreign key constraints on connection.
    
    SQLite doesn't enforce foreign keys by default, so we need to
    enable them explicitly for each connection.
    
    Args:
        dbapi_conn: The database connection.
        connection_record: Connection record metadata.
    """
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
