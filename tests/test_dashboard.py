"""
Tests unitaires complémentaires — metric_calculator.py & analytics.py
Couvre les fonctions non testées dans les fichiers existants.
"""

import pytest
from unittest.mock import patch, MagicMock


# ==============================================================
# HELPERS
# ==============================================================

def make_cursor_mock(fetchone=None, fetchall=None):
    cursor = MagicMock()
    cursor.fetchone.return_value = fetchone
    cursor.fetchall.return_value = fetchall or []
    return cursor


def make_conn_mock(cursor):
    conn = MagicMock()
    conn.__enter__ = MagicMock(return_value=conn)
    conn.__exit__ = MagicMock(return_value=False)
    conn.cursor.return_value = cursor
    return conn



# ==============================================================
# TESTS — get_teacher_stats
# ==============================================================

class TestGetTeacherStats:

    @patch("analytics.from_json")
    @patch("analytics.get_db_connection")
    def test_enseignant_inexistant_retourne_none(self, mock_db, mock_json):
        """Retourne None si l'enseignant n'existe pas."""
        cursor = make_cursor_mock(fetchone=None)
        mock_db.return_value = make_conn_mock(cursor)

        from analytics import get_teacher_stats
        result = get_teacher_stats(999)
        assert result is None

    @patch("analytics.from_json")
    @patch("analytics.get_db_connection")
    def test_retourne_dict_avec_disciplines(self, mock_db, mock_json):
        """Le résultat contient bien la clé 'disciplines'."""
        cursor = make_cursor_mock(
            fetchone={"discipline": '["Programmation"]'},
        )
        mock_json.return_value = ["Programmation"]
        cursor.fetchone.side_effect = [
            {"discipline": '["Programmation"]'},
            {"moyenne": 0.75, "nb_aav": 5, "nb_apprenants": 10}
        ]
        mock_db.return_value = make_conn_mock(cursor)

        from analytics import get_teacher_stats
        result = get_teacher_stats(1)

        assert result is not None
        assert "disciplines" in result

    @patch("analytics.from_json")
    @patch("analytics.get_db_connection")
    def test_retourne_moyenne_et_compteurs(self, mock_db, mock_json):
        """Le résultat contient moyenne, nb_aav et nb_apprenants."""
        mock_json.return_value = ["Programmation", "Algorithmique"]
        cursor = MagicMock()
        cursor.fetchone.side_effect = [
            {"discipline": '["Programmation", "Algorithmique"]'},
            {"moyenne": 0.68, "nb_aav": 8, "nb_apprenants": 15}
        ]
        conn = make_conn_mock(cursor)
        mock_db.return_value = conn

        from analytics import get_teacher_stats
        result = get_teacher_stats(2)

        assert result["moyenne"] == 0.68
        assert result["nb_aav"] == 8
        assert result["nb_apprenants"] == 15


# ==============================================================
# TESTS — get_discipline_stats
# ==============================================================

class TestGetDisciplineStats:

    @patch("analytics.get_db_connection")
    def test_retourne_dict_avec_champs_attendus(self, mock_db):
        """Retourne un dict avec moyenne, moyenne_covering et nb."""
        row = {"moyenne": 0.70, "moyenne_covering": 0.85, "nb": 5}
        cursor = make_cursor_mock(fetchone=row)
        mock_db.return_value = make_conn_mock(cursor)

        from analytics import get_discipline_stats
        result = get_discipline_stats("Programmation")

        assert "moyenne" in result
        assert "moyenne_covering" in result
        assert "nb" in result

    @patch("analytics.get_db_connection")
    def test_valeurs_correctes(self, mock_db):
        """Les valeurs retournées correspondent aux données en base."""
        row = {"moyenne": 0.65, "moyenne_covering": 0.80, "nb": 10}
        cursor = make_cursor_mock(fetchone=row)
        mock_db.return_value = make_conn_mock(cursor)

        from analytics import get_discipline_stats
        result = get_discipline_stats("Algorithmique")

        assert result["moyenne"] == 0.65
        assert result["nb"] == 10

    @patch("analytics.get_db_connection")
    def test_requete_filtre_par_discipline(self, mock_db):
        """La requête SQL passe bien le nom de discipline en paramètre."""
        cursor = make_cursor_mock(fetchone={"moyenne": 0.0, "moyenne_covering": 0.0, "nb": 0})
        mock_db.return_value = make_conn_mock(cursor)

        from analytics import get_discipline_stats
        get_discipline_stats("Mathématiques")

        args = cursor.execute.call_args[0]
        assert args[1] == ("Mathématiques",)

    @patch("analytics.get_db_connection")
    def test_discipline_sans_aav_retourne_zeros(self, mock_db):
        """Une discipline sans AAV retourne des compteurs à 0."""
        row = {"moyenne": 0.0, "moyenne_covering": None, "nb": 0}
        cursor = make_cursor_mock(fetchone=row)
        mock_db.return_value = make_conn_mock(cursor)

        from analytics import get_discipline_stats
        result = get_discipline_stats("DisciplineInconnue")

        assert result["nb"] == 0
        assert result["moyenne"] == 0.0


# ==============================================================
# TESTS — get_ontology_cov
# ==============================================================

class TestGetOntologyCov:

    @patch("analytics.from_json")
    @patch("analytics.get_db_connection")
    def test_ontologie_inexistante_retourne_none(self, mock_db, mock_json):
        """Retourne None si l'ontologie n'existe pas."""
        cursor = make_cursor_mock(fetchone=None)
        mock_db.return_value = make_conn_mock(cursor)

        from analytics import get_ontology_cov
        result = get_ontology_cov(999)
        assert result is None

    @patch("analytics.from_json")
    @patch("analytics.get_db_connection")
    def test_retourne_dict_avec_nb_aav_et_moyenne(self, mock_db, mock_json):
        """Le résultat contient nb_aav et moyenne_covering."""
        mock_json.return_value = [1, 2, 3]
        cursor = MagicMock()
        cursor.fetchone.side_effect = [
            {"aavs_ids_actifs": "[1,2,3]"},
            {"nb_aav": 3, "moyenne_covering": 0.82}
        ]
        conn = make_conn_mock(cursor)
        mock_db.return_value = conn

        from analytics import get_ontology_cov
        result = get_ontology_cov(1)

        assert result is not None
        assert "nb_aav" in result
        assert "moyenne_covering" in result

    @patch("analytics.from_json")
    @patch("analytics.get_db_connection")
    def test_moyenne_covering_correcte(self, mock_db, mock_json):
        """La moyenne de couverture retournée est bien celle de la base."""
        mock_json.return_value = [1, 2, 3, 4, 5]
        cursor = MagicMock()
        cursor.fetchone.side_effect = [
            {"aavs_ids_actifs": "[1,2,3,4,5]"},
            {"nb_aav": 5, "moyenne_covering": 0.91}
        ]
        conn = make_conn_mock(cursor)
        mock_db.return_value = conn

        from analytics import get_ontology_cov
        result = get_ontology_cov(2)

        assert result["moyenne_covering"] == pytest.approx(0.91)
        assert result["nb_aav"] == 5

    @patch("analytics.from_json")
    @patch("analytics.get_db_connection")
    def test_placeholders_generes_correctement(self, mock_db, mock_json):
        """Le bon nombre de placeholders '?' est généré pour la clause IN."""
        mock_json.return_value = [1, 2, 3]
        cursor = MagicMock()
        cursor.fetchone.side_effect = [
            {"aavs_ids_actifs": "[1,2,3]"},
            {"nb_aav": 3, "moyenne_covering": 0.80}
        ]
        conn = make_conn_mock(cursor)
        mock_db.return_value = conn

        from analytics import get_ontology_cov
        get_ontology_cov(1)

        # Le deuxième appel SQL doit contenir 3 placeholders
        second_call_sql = cursor.execute.call_args_list[1][0][0]
        assert second_call_sql.count("?") == 3
