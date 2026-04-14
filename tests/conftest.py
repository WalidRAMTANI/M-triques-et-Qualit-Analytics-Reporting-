"""
Configuration pytest and global helpers for tests.
Provides reusable mocks for SQLAlchemy ORM.
"""

from unittest.mock import MagicMock, patch
import pytest
import os
from app.database import init_database, SessionLocal, ApprenantModel


def make_orm_query_mock(scalar=None, first=None, all_results=None):
    """
    Creates a complete mock for SQLAlchemy ORM:
    - session.query(...) 
    - .filter() 
    - .scalar(), .first(), .all()
    """
    query_result = MagicMock()
    query_result.scalar.return_value = scalar
    query_result.first.return_value = first
    query_result.all.return_value = all_results if all_results is not None else []
    
    # Chaining
    query_result.filter.return_value = query_result
    query_result.join.return_value = query_result
    query_result.outerjoin.return_value = query_result
    query_result.order_by.return_value = query_result
    
    session = MagicMock()
    session.__enter__ = MagicMock(return_value=session)
    session.__exit__ = MagicMock(return_value=False)
    session.query.return_value = query_result
    
    return session, query_result


# Remove old test database if it exists to start fresh
if os.path.exists('platonAAV.db'):
    try:
        os.remove('platonAAV.db')
    except Exception as e:
        print(f"Warning: could not remove platonAAV.db: {e}")

# Initialize database with all tables
init_database()

def pytest_sessionfinish(session, exitstatus):
    """Cleanup after all tests finish."""
    pass

