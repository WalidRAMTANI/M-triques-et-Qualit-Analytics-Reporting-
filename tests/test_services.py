"""
Tests unitaires pour alert_detector.py — Projet PlatonAAV
Données de test basées sur le dump SQL fourni.
"""

import pytest
from unittest.mock import patch, MagicMock


# ==============================================================
# FIXTURES — Données issues du dump SQL
# ==============================================================

AAVS = [
    {"id_aav": i, "nom": nom} for i, nom in [
        (1, "Types entiers"), (2, "Type caractère"), (3, "Types flottants"),
        (4, "Déclaration de variables"), (5, "Opérateurs arithmétiques"),
        (6, "Opérateurs de comparaison"), (7, "Opérateurs logiques"),
        (8, "Structure if-else"), (9, "Boucle while"), (10, "Boucle for"),
        (11, "Fonctions"), (12, "Paramètres de fonctions"), (13, "Tableaux"),
        (14, "Chaînes de caractères"), (15, "Pointeurs"), (16, "Allocation mémoire"),
        (17, "Structures (struct)"), (18, "Fichiers"),
        (19, "Types de base"), (20, "Flux de contrôle"),
    ]
]

APPRENANTS = [
    {"id_apprenant": 1, "nom_utilisateur": "alice_debutante"},
    {"id_apprenant": 2, "nom_utilisateur": "bob_progressif"},
    {"id_apprenant": 3, "nom_utilisateur": "charlie_expert"},
    {"id_apprenant": 4, "nom_utilisateur": "david_bloque"},
    {"id_apprenant": 5, "nom_utilisateur": "eve_revision"},
]

TENTATIVES_PAR_AAV = {
    1: [
        {"score_obtenu": 0.70}, {"score_obtenu": 0.80}, {"score_obtenu": 0.85},
        {"score_obtenu": 0.80}, {"score_obtenu": 0.90}, {"score_obtenu": 1.00},
    ],
    2: [
        {"score_obtenu": 0.50}, {"score_obtenu": 0.60},
        {"score_obtenu": 0.20}, {"score_obtenu": 0.15},
        {"score_obtenu": 0.30}, {"score_obtenu": 0.25},
    ],
    5: [
        {"score_obtenu": 0.40}, {"score_obtenu": 0.45},
        {"score_obtenu": 0.20}, {"score_obtenu": 0.25}, {"score_obtenu": 0.15},
    ],
    6: [{"score_obtenu": 0.30}, {"score_obtenu": 0.10}, {"score_obtenu": 0.10}],
    15: [
        {"score_obtenu": 0.40}, {"score_obtenu": 0.30}, {"score_obtenu": 0.50},
        {"score_obtenu": 0.20}, {"score_obtenu": 0.60}, {"score_obtenu": 0.40},
        {"score_obtenu": 0.30}, {"score_obtenu": 0.50},
    ],
    7: [], 8: [], 9: [], 10: [], 11: [], 12: [], 13: [],
    14: [], 16: [], 17: [], 18: [], 19: [], 20: [],
    3: [], 4: [],
}

NIVEAUX_MAITRISE = {
    1: [],
    2: [0.85, 0.60, 0.45, 0.30],
    3: [1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 0.90, 0.75, 0.60, 0.50, 0.40, 0.30, 0.20, 0.00],
    4: [0.90, 0.25, 0.20, 0.10],
    5: [0.95, 0.90, 0.88, 0.85, 0.82],
}

AAVS_BLOQUES = {1: 0, 2: 4, 3: 8, 4: 3, 5: 5}


# ==============================================================
# HELPERS — interface SQLAlchemy
# ==============================================================

def make_row_mock(data: dict):
    """Crée un mock de ligne SQLAlchemy avec ._mapping."""
    row = MagicMock()
    row._mapping = data
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


