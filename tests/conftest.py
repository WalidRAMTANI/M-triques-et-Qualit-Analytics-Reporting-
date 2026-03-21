"""
Configuration pytest et helpers globaux pour les tests.
Fournit des mocks réutilisables pour SQLAlchemy ORM.

⚠️ ADAPTATION: Convertit les mocks SQL brut (session.execute) 
en mocks ORM (session.query) automatiquement.
"""

from unittest.mock import MagicMock, patch
import pytest


def make_orm_query_mock(scalar=None, first=None, all_results=None):
    """
    Crée un mock complet pour SQLAlchemy ORM:
    - session.query(...) 
    - .filter() 
    - .scalar(), .first(), .all()
    """
    query_result = MagicMock()
    query_result.scalar.return_value = scalar
    query_result.first.return_value = first
    query_result.all.return_value = all_results if all_results is not None else []
    
    # Chaîning
    query_result.filter.return_value = query_result
    query_result.join.return_value = query_result
    query_result.outerjoin.return_value = query_result
    query_result.order_by.return_value = query_result
    
    session = MagicMock()
    session.__enter__ = MagicMock(return_value=session)
    session.__exit__ = MagicMock(return_value=False)
    session.query.return_value = query_result
    
    return session, query_result
