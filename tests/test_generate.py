"""
Tests unitaires pour services/report_generator.py — Projet PlatonAAV
Données de test basées sur le dump SQL fourni.
"""

import pytest
from datetime import datetime
import base64
from unittest.mock import patch, MagicMock


# ==============================================================
# DONNÉES DE TEST (issues du dump SQL)
# ==============================================================

AAV_1 = {
    "id_aav": 1,
    "nom": "Types entiers",
    "discipline": "Programmation",
    "description_markdown": "Comprendre et utiliser les types entiers en C",
    "libelle_integration": "les types entiers (int, short, long)"
}

AAV_5 = {
    "id_aav": 5,
    "nom": "Opérateurs arithmétiques",
    "discipline": "Programmation",
    "description_markdown": "Utiliser les opérateurs arithmétiques",
    "libelle_integration": "les opérateurs arithmétiques (+, -, *, /, %)"
}

STUDENT_BOB = {
    "id_apprenant": 2,
    "nom": "bob_progressif",
    "email": "bob@example.com",
    "date_inscription": "2026-01-10 09:00:00",
    "derniere_connexion": "2026-02-21 10:15:00"
}

TENTATIVES_BOB = [
    {"id_aav": 1, "nom": "Types entiers",          "score_obtenu": 0.85, "date_tentative": "2026-02-20"},
    {"id_aav": 2, "nom": "Type caractère",          "score_obtenu": 0.60, "date_tentative": "2026-02-19"},
    {"id_aav": 5, "nom": "Opérateurs arithmétiques","score_obtenu": 0.45, "date_tentative": "2026-02-18"},
]


# ==============================================================
# HELPERS — interface SQLAlchemy
# ==============================================================

def make_row_mock(data: dict):
    """Crée un mock de ligne SQLAlchemy avec ._mapping."""
    row = MagicMock()
    row._mapping = data
    # Permet aussi l'accès direct via row["key"] pour la compat
    row.__getitem__ = lambda self, k: data[k]
    return row


def make_session_mock(scalar=None, fetchone=None, fetchall=None, first=None, all_results=None):
    """
    Crée un mock de session universal (ORM + SQL brut).
    - Si first/all_results: mode ORM avec .first() / .all()
    - Si scalar: mode ORM avec .scalar()
    - Si fetchone/fetchall: mode SQL brut (session.execute) - LEGACY
    """
    # Mode ORM
    if scalar is not None or first is not None or all_results is not None:
        query_result = MagicMock()
        
        # Configurer .scalar()
        query_result.scalar.return_value = scalar
        
        # Convertir les dicts en objets avec attributs (pour ORM)
        if isinstance(first, dict):
            first_obj = MagicMock()
            for key, value in first.items():
                setattr(first_obj, key, value)
            query_result.first.return_value = first_obj
        else:
            query_result.first.return_value = first
        
        if isinstance(all_results, list):
            all_objs = []
            for item in all_results:
                if isinstance(item, dict):
                    obj = MagicMock()
                    for key, value in item.items():
                        setattr(obj, key, value)
                    all_objs.append(obj)
                else:
                    all_objs.append(item)
            query_result.all.return_value = all_objs
        else:
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
    
    # Mode SQL brut (legacy)
    result = MagicMock()
    result.scalar.return_value = scalar
    result.fetchone.return_value = fetchone
    result.fetchall.return_value = fetchall if fetchall is not None else []

    session = MagicMock()
    session.__enter__ = MagicMock(return_value=session)
    session.__exit__ = MagicMock(return_value=False)
    session.execute.return_value = result
    return session, result


