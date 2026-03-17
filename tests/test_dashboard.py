"""
Tests unitaires complémentaires — metric_calculator.py & analytics.py
Couvre les fonctions non testées dans les fichiers existants.
"""

import pytest
from unittest.mock import patch, MagicMock


# ==============================================================
# HELPERS
# ==============================================================

def make_session_mock(get_return=None, first_return=None):
    session = MagicMock()
    session.__enter__.return_value = session
    session.__exit__.return_value = False
    
    session.get.return_value = get_return
        
    query = MagicMock()
    session.query.return_value = query
    query.select_from.return_value = query
    query.join.return_value = query
    query.filter.return_value = query
    
    if first_return is not None:
        query.first.return_value = first_return
        
    return session


# ==============================================================
# TESTS — get_teacher_stats
# ==============================================================

class TestGetTeacherStats:

    @patch("services.dashboard_data.get_db_session")
    def test_enseignant_inexistant_retourne_none(self, mock_db):
        """Retourne None si l'enseignant n'existe pas."""
        mock_db.return_value = make_session_mock(get_return=None)

        from services.dashboard_data import get_teacher_stats
        result = get_teacher_stats(999)
        assert result is None

    @patch("services.dashboard_data.get_db_session")
    def test_retourne_dict_avec_disciplines(self, mock_db):
        """Le résultat contient bien la clé 'disciplines'."""
        enseignant = {"id_enseignant": 1, "discipline": ["Programmation"]}
        res = MagicMock(); res.moyenne = 0.75; res.nb_aav = 5; res.nb_apprenants = 10
        mock_db.return_value = make_session_mock(get_return=enseignant, first_return=res)

        from services.dashboard_data import get_teacher_stats
        result = get_teacher_stats(1)

        assert result is not None
        assert "disciplines" in result


# ==============================================================
# TESTS — get_discipline_stats
# ==============================================================

class TestGetDisciplineStats:

    @patch("services.dashboard_data.get_db_session")
    def test_retourne_dict_avec_champs_attendus(self, mock_db):
        """Retourne un dict avec moyenne, moyenne_covering et nb."""
        res = MagicMock(); res.moyenne = 0.70; res.moyenne_covering = 0.85; res.nb = 5
        mock_db.return_value = make_session_mock(first_return=res)

        from services.dashboard_data import get_discipline_stats
        result = get_discipline_stats("Programmation")

        assert "moyenne" in result
        assert "moyenne_covering" in result
        assert "nb" in result


# ==============================================================
# TESTS — get_ontology_cov
# ==============================================================

class TestGetOntologyCov:

    @patch("services.dashboard_data.get_db_session")
    def test_ontologie_inexistante_retourne_none(self, mock_db):
        """Retourne None si l'ontologie n'existe pas."""
        mock_db.return_value = make_session_mock(get_return=None)

        from services.dashboard_data import get_ontology_cov
        result = get_ontology_cov(999)
        assert result is None

    @patch("services.dashboard_data.get_db_session")
    def test_retourne_dict_avec_nb_aav_et_moyenne(self, mock_db):
        """Le résultat contient nb_aav et moyenne_covering."""
        onto = {"id_reference": 1, "aavs_ids_actifs": [1, 2, 3]}
        res = MagicMock(); res.nb_aav = 3; res.moyenne_covering = 0.82
        mock_db.return_value = make_session_mock(get_return=onto, first_return=res)

        from services.dashboard_data import get_ontology_cov
        result = get_ontology_cov(1)

        assert result is not None
        assert "nb_aav" in result
        assert "moyenne_covering" in result
