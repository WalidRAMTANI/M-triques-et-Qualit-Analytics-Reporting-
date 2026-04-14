"""
Tests unitaires complémentaires — metric_calculator.py & analytics.py
Couvre les fonctions non testées dans les fichiers existants.
"""

import pytest
from unittest.mock import patch, MagicMock


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


def make_session_multi_mock(execute_results: list):
    """
    Crée une session dont execute() retourne des résultats différents
    à chaque appel successif (utile pour les fonctions qui font 2+ requêtes).
    Each item in execute_results is a dict: {scalar, fetchone, fetchall}
    """
    def make_result(spec):
        result = MagicMock()
        result.scalar.return_value = spec.get("scalar")
        fo = spec.get("fetchone")
        result.fetchone.return_value = make_row_mock(fo) if isinstance(fo, dict) else fo
        fa = spec.get("fetchall")
        result.fetchall.return_value = (
            [make_row_mock(r) if isinstance(r, dict) else r for r in fa]
            if fa is not None else []
        )
        return result

    results = [make_result(s) for s in execute_results]

    session = MagicMock()
    session.__enter__ = MagicMock(return_value=session)
    session.__exit__ = MagicMock(return_value=False)
    session.execute.side_effect = results
    return session


# ==============================================================
# TESTS — get_teacher_stats
# ==============================================================

# ==============================================================
# TESTS — get_teacher_stats
# ==============================================================

class TestGetTeacherStats:

    @patch("app.services.dashboard_data.get_db_connection")
    def test_retourne_stats_enseignant(self, mock_db):
        """Le résultat contient les stats attendues."""
        # Mock teacher
        enseignant = MagicMock()
        enseignant.id_enseignant = 1
        enseignant.nom = "John"
        enseignant.discipline = ["Maths"]
        
        # Mock stats
        stats = MagicMock()
        stats.nb_aav = 5
        stats.nb_apprenants = 10
        stats.moyenne = 0.75
        
        session = MagicMock()
        session.__enter__.return_value = session
        
        # Chain returns the same mock until .first() or .scalar()
        query_mock = session.query.return_value
        query_mock.filter.return_value = query_mock
        query_mock.outerjoin.return_value = query_mock
        query_mock.join.return_value = query_mock
        
        query_mock.first.side_effect = [enseignant, stats]
        query_mock.scalar.return_value = 2 # alert_count

        
        mock_db.return_value = session

        from app.services.dashboard_data import get_teacher_stats
        result = get_teacher_stats(1)

        assert result is not None
        assert result["aavs_geres"] == 5
        assert result["taux_succes_moyen"] == 0.75
        assert result["alertes_actives"] == 2


# ==============================================================
# TESTS — get_discipline_stats
# ==============================================================

class TestGetDisciplineStats:

    @patch("app.services.dashboard_data.get_db_connection")
    def test_retourne_dict_avec_champs_attendus(self, mock_db):
        """Retourne un dict avec les stats disciplinaires."""
        stats = MagicMock()
        stats.moyenne = 0.70
        stats.nb_aav = 5
        stats.nb_apprenants = 10
        
        session = MagicMock()
        session.__enter__.return_value = session
        query_mock = session.query.return_value
        query_mock.filter.return_value = query_mock
        query_mock.outerjoin.return_value = query_mock
        
        query_mock.first.return_value = stats
        query_mock.scalar.return_value = 3 # activites_count

        
        mock_db.return_value = session

        from app.services.dashboard_data import get_discipline_stats
        result = get_discipline_stats("Programmation")

        assert result["discipline"] == "Programmation"
        assert result["aavs_total"] == 5
        assert result["taux_succes_moyen"] == 0.70
        assert result["activites_recentes"] == 3

    @patch("app.services.dashboard_data.get_db_connection")
    def test_discipline_sans_aav_retourne_zeros(self, mock_db):
        """Une discipline sans AAV retourne des compteurs à 0."""
        session = MagicMock()
        session.__enter__.return_value = session
        query_mock = session.query.return_value
        query_mock.filter.return_value = query_mock
        query_mock.outerjoin.return_value = query_mock
        
        query_mock.first.return_value = None
        query_mock.scalar.return_value = 0

        
        mock_db.return_value = session

        from app.services.dashboard_data import get_discipline_stats
        result = get_discipline_stats("DisciplineInconnue")

        assert result["aavs_total"] == 0
        assert result["taux_succes_moyen"] == 0.0


# ==============================================================
# TESTS — get_ontology_cov
# ==============================================================

class TestGetOntologyCov:

    @patch("app.services.dashboard_data.get_db_connection")
    def test_retourne_dict_avec_nb_aav_et_moyenne(self, mock_db):
        """Le résultat contient nb_aav et moyenne_covering."""
        ontologie = MagicMock()
        ontologie.aavs_ids_actifs = [1, 2, 3]
        
        stats = MagicMock()
        stats.nb_aav = 3
        stats.moyenne_covering = 0.82
        
        session = MagicMock()
        session.__enter__.return_value = session
        query_mock = session.query.return_value
        query_mock.filter.return_value = query_mock
        
        query_mock.first.side_effect = [ontologie, stats]

        
        mock_db.return_value = session

        from app.services.dashboard_data import get_ontology_cov
        result = get_ontology_cov(1)

        assert result is not None
        assert result["nb_aav"] == 3
        assert result["moyenne_covering"] == 0.82