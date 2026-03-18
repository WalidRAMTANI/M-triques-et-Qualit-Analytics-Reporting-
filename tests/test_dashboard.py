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


def make_session_mock(scalar=None, fetchone=None, fetchall=None):
    """
    Crée un mock de session SQLAlchemy.
    Supporte plusieurs appels successifs à execute() via side_effect.
    """
    result = MagicMock()
    result.scalar.return_value = scalar
    result.fetchone.return_value = make_row_mock(fetchone) if isinstance(fetchone, dict) else fetchone
    result.fetchall.return_value = (
        [make_row_mock(r) if isinstance(r, dict) else r for r in fetchall]
        if fetchall is not None else []
    )

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

class TestGetTeacherStats:

    @patch("services.dashboard_data.get_db_session")
    def test_enseignant_inexistant_retourne_none(self, mock_db):
        """Retourne None si l'enseignant n'existe pas."""
        session = make_session_multi_mock([
            {"fetchone": None},  # première requête: SELECT discipline
        ])
        mock_db.return_value = session

        from services.dashboard_data import get_teacher_stats
        result = get_teacher_stats(999)
        assert result is None

    @patch("services.dashboard_data.get_db_session")
    def test_retourne_dict_avec_disciplines(self, mock_db):
        """Le résultat contient bien la clé 'disciplines'."""
        mock_json.return_value = ["Programmation"]
        session = make_session_multi_mock([
            {"fetchone": {"discipline": '["Programmation"]'}},
            {"fetchone": {"moyenne": 0.75, "nb_aav": 5, "nb_apprenants": 10}},
        ])
        mock_db.return_value = session

        from services.dashboard_data import get_teacher_stats
        result = get_teacher_stats(1)

        assert result is not None
        assert "disciplines" in result

    @patch("services.dashboard_data.from_json")
    @patch("services.dashboard_data.get_db_connection")
    def test_retourne_moyenne_et_compteurs(self, mock_db, mock_json):
        """Le résultat contient moyenne, nb_aav et nb_apprenants."""
        mock_json.return_value = ["Programmation", "Algorithmique"]
        session = make_session_multi_mock([
            {"fetchone": {"discipline": '["Programmation", "Algorithmique"]'}},
            {"fetchone": {"moyenne": 0.68, "nb_aav": 8, "nb_apprenants": 15}},
        ])
        mock_db.return_value = session

        from services.dashboard_data import get_teacher_stats
        result = get_teacher_stats(2)

        assert result["moyenne"] == 0.68
        assert result["nb_aav"] == 8
        assert result["nb_apprenants"] == 15


# ==============================================================
# TESTS — get_discipline_stats
# ==============================================================

class TestGetDisciplineStats:

    @patch("services.dashboard_data.get_db_session")
    def test_retourne_dict_avec_champs_attendus(self, mock_db):
        """Retourne un dict avec moyenne, moyenne_covering et nb."""
        session, _ = make_session_mock(
            fetchone={"moyenne": 0.70, "moyenne_covering": 0.85, "nb": 5}
        )
        mock_db.return_value = session

        from services.dashboard_data import get_discipline_stats
        result = get_discipline_stats("Programmation")

        assert "moyenne" in result
        assert "moyenne_covering" in result
        assert "nb" in result

    @patch("services.dashboard_data.get_db_connection")
    def test_valeurs_correctes(self, mock_db):
        """Les valeurs retournées correspondent aux données en base."""
        session, _ = make_session_mock(
            fetchone={"moyenne": 0.65, "moyenne_covering": 0.80, "nb": 10}
        )
        mock_db.return_value = session

        from services.dashboard_data import get_discipline_stats
        result = get_discipline_stats("Algorithmique")

        assert result["moyenne"] == 0.65
        assert result["nb"] == 10

    @patch("services.dashboard_data.get_db_connection")
    def test_requete_filtre_par_discipline(self, mock_db):
        """La requête SQL passe bien le nom de discipline en paramètre."""
        session, _ = make_session_mock(
            fetchone={"moyenne": 0.0, "moyenne_covering": 0.0, "nb": 0}
        )
        mock_db.return_value = session

        from services.dashboard_data import get_discipline_stats
        get_discipline_stats("Mathématiques")

        call_args = session.execute.call_args
        assert call_args[0][1]["discipline"] == "Mathématiques"

    @patch("services.dashboard_data.get_db_connection")
    def test_discipline_sans_aav_retourne_zeros(self, mock_db):
        """Une discipline sans AAV retourne des compteurs à 0."""
        session, _ = make_session_mock(
            fetchone={"moyenne": 0.0, "moyenne_covering": None, "nb": 0}
        )
        mock_db.return_value = session

        from services.dashboard_data import get_discipline_stats
        result = get_discipline_stats("DisciplineInconnue")

        assert result["nb"] == 0
        assert result["moyenne"] == 0.0


# ==============================================================
# TESTS — get_ontology_cov
# ==============================================================

class TestGetOntologyCov:

    @patch("services.dashboard_data.get_db_session")
    def test_ontologie_inexistante_retourne_none(self, mock_db):
        """Retourne None si l'ontologie n'existe pas."""
        session = make_session_multi_mock([
            {"fetchone": None},
        ])
        mock_db.return_value = session

        from services.dashboard_data import get_ontology_cov
        result = get_ontology_cov(999)
        assert result is None

    @patch("services.dashboard_data.get_db_session")
    def test_retourne_dict_avec_nb_aav_et_moyenne(self, mock_db):
        """Le résultat contient nb_aav et moyenne_covering."""
        mock_json.return_value = [1, 2, 3]
        session = make_session_multi_mock([
            {"fetchone": {"aavs_ids_actifs": "[1,2,3]"}},
            {"fetchone": {"nb_aav": 3, "moyenne_covering": 0.82}},
        ])
        mock_db.return_value = session

        from services.dashboard_data import get_ontology_cov
        result = get_ontology_cov(1)

        assert result is not None
        assert "nb_aav" in result
        assert "moyenne_covering" in result

    @patch("services.dashboard_data.from_json")
    @patch("services.dashboard_data.get_db_connection")
    def test_moyenne_covering_correcte(self, mock_db, mock_json):
        """La moyenne de couverture retournée est bien celle de la base."""
        mock_json.return_value = [1, 2, 3, 4, 5]
        session = make_session_multi_mock([
            {"fetchone": {"aavs_ids_actifs": "[1,2,3,4,5]"}},
            {"fetchone": {"nb_aav": 5, "moyenne_covering": 0.91}},
        ])
        mock_db.return_value = session

        from services.dashboard_data import get_ontology_cov
        result = get_ontology_cov(2)

        assert result["moyenne_covering"] == pytest.approx(0.91)
        assert result["nb_aav"] == 5

    @patch("services.dashboard_data.from_json")
    @patch("services.dashboard_data.get_db_connection")
    def test_placeholders_generes_correctement(self, mock_db, mock_json):
        """Les bons paramètres nommés sont générés pour la clause IN."""
        mock_json.return_value = [1, 2, 3]
        session = make_session_multi_mock([
            {"fetchone": {"aavs_ids_actifs": "[1,2,3]"}},
            {"fetchone": {"nb_aav": 3, "moyenne_covering": 0.80}},
        ])
        mock_db.return_value = session

        from services.dashboard_data import get_ontology_cov
        get_ontology_cov(1)

        # Le deuxième appel SQL doit contenir 3 paramètres nommés :id0, :id1, :id2
        second_call_sql = str(session.execute.call_args_list[1][0][0])
        assert ":id0" in second_call_sql
        assert ":id1" in second_call_sql
        assert ":id2" in second_call_sql