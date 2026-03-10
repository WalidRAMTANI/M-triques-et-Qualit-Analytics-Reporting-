"""
Tests unitaires pour metric_calculator.py — Projet PlatonAAV
Données de test basées sur le dump SQL fourni.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


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
# TESTS — count_exercices
# ==============================================================

class TestCountExercices:

    @patch("metric_calculator.from_json")
    @patch("metric_calculator.get_db_connection")
    def test_aav_1_deux_exercices(self, mock_db, mock_json):
        """AAV 1 a ids_exercices = [101, 102] → 2."""
        cursor = make_cursor_mock(fetchone={"ids_exercices": "[101, 102]"})
        mock_db.return_value = make_conn_mock(cursor)
        mock_json.return_value = [101, 102]

        from metric_calculator import count_exercices
        assert count_exercices(1) == 2

    @patch("metric_calculator.from_json")
    @patch("metric_calculator.get_db_connection")
    def test_aav_inexistant_retourne_zero(self, mock_db, mock_json):
        cursor = make_cursor_mock(fetchone=None)
        mock_db.return_value = make_conn_mock(cursor)

        from metric_calculator import count_exercices
        assert count_exercices(999) == 0

    @patch("metric_calculator.from_json")
    @patch("metric_calculator.get_db_connection")
    def test_ids_exercices_null_retourne_zero(self, mock_db, mock_json):
        cursor = make_cursor_mock(fetchone={"ids_exercices": None})
        mock_db.return_value = make_conn_mock(cursor)

        from metric_calculator import count_exercices
        assert count_exercices(5) == 0

    @patch("metric_calculator.from_json")
    @patch("metric_calculator.get_db_connection")
    def test_aav_composite_19_six_exercices(self, mock_db, mock_json):
        """AAV 19 (composite) a 6 exercices: [101,102,103,104,105,106]."""
        cursor = make_cursor_mock(fetchone={"ids_exercices": "[101,102,103,104,105,106]"})
        mock_db.return_value = make_conn_mock(cursor)
        mock_json.return_value = [101, 102, 103, 104, 105, 106]

        from metric_calculator import count_exercices
        assert count_exercices(19) == 6


# ==============================================================
# TESTS — count_prompts
# ==============================================================

class TestCountPrompts:

    @patch("metric_calculator.from_json")
    @patch("metric_calculator.get_db_connection")
    def test_aav_1_un_prompt(self, mock_db, mock_json):
        """AAV 1 a prompts_fabrication_ids = [1] → 1."""
        cursor = make_cursor_mock(fetchone={"prompts_fabrication_ids": "[1]"})
        mock_db.return_value = make_conn_mock(cursor)
        mock_json.return_value = [1]

        from metric_calculator import count_prompts
        assert count_prompts(1) == 1

    @patch("metric_calculator.from_json")
    @patch("metric_calculator.get_db_connection")
    def test_aav_inexistant_retourne_zero(self, mock_db, mock_json):
        cursor = make_cursor_mock(fetchone=None)
        mock_db.return_value = make_conn_mock(cursor)

        from metric_calculator import count_prompts
        assert count_prompts(999) == 0

    @patch("metric_calculator.from_json")
    @patch("metric_calculator.get_db_connection")
    def test_prompts_null_retourne_zero(self, mock_db, mock_json):
        cursor = make_cursor_mock(fetchone={"prompts_fabrication_ids": None})
        mock_db.return_value = make_conn_mock(cursor)

        from metric_calculator import count_prompts
        assert count_prompts(3) == 0

    @patch("metric_calculator.from_json")
    @patch("metric_calculator.get_db_connection")
    def test_aav_19_trois_prompts(self, mock_db, mock_json):
        """AAV 19 (composite) référence les prompts [1, 2, 3]."""
        cursor = make_cursor_mock(fetchone={"prompts_fabrication_ids": "[1, 2, 3]"})
        mock_db.return_value = make_conn_mock(cursor)
        mock_json.return_value = [1, 2, 3]

        from metric_calculator import count_prompts
        assert count_prompts(19) == 3


# ==============================================================
# TESTS — diversity_evaluation_types
# ==============================================================

class TestDiversityEvaluationTypes:

    @patch("metric_calculator.get_db_connection")
    def test_aav_avec_un_type(self, mock_db):
        """AAV 1 a un seul type: 'Calcul Automatisé' → 1."""
        cursor = make_cursor_mock(fetchone=(1,))
        mock_db.return_value = make_conn_mock(cursor)

        from metric_calculator import diversity_evaluation_types
        assert diversity_evaluation_types(1) == 1

    @patch("metric_calculator.get_db_connection")
    def test_aav_inexistant_retourne_zero(self, mock_db):
        cursor = make_cursor_mock(fetchone=None)
        mock_db.return_value = make_conn_mock(cursor)

        from metric_calculator import diversity_evaluation_types
        assert diversity_evaluation_types(999) == 0

    @patch("metric_calculator.get_db_connection")
    def test_retourne_entier(self, mock_db):
        cursor = make_cursor_mock(fetchone=(2,))
        mock_db.return_value = make_conn_mock(cursor)

        from metric_calculator import diversity_evaluation_types
        result = diversity_evaluation_types(8)
        assert isinstance(result, int)


# ==============================================================
# TESTS — get_all_attempts_for_aav
# ==============================================================

class TestGetAllAttemptsForAAV:

    @patch("metric_calculator.get_db_connection")
    def test_aav_1_retourne_six_tentatives(self, mock_db):
        """AAV 1 a 6 tentatives dans le dump."""
        rows = [
            {"id": i, "id_aav_cible": 1, "score_obtenu": s}
            for i, s in enumerate([0.70, 0.80, 0.85, 0.80, 0.90, 1.00], 1)
        ]
        cursor = make_cursor_mock(fetchall=rows)
        mock_db.return_value = make_conn_mock(cursor)

        from metric_calculator import get_all_attempts_for_aav
        result = get_all_attempts_for_aav(1)

        assert len(result) == 6
        assert result[0]["score_obtenu"] == 0.70

    @patch("metric_calculator.get_db_connection")
    def test_aav_sans_tentatives_retourne_liste_vide(self, mock_db):
        """AAV 7 n'a aucune tentative."""
        cursor = make_cursor_mock(fetchall=[])
        mock_db.return_value = make_conn_mock(cursor)

        from metric_calculator import get_all_attempts_for_aav
        assert get_all_attempts_for_aav(7) == []

    @patch("metric_calculator.get_db_connection")
    def test_retourne_liste_de_dicts(self, mock_db):
        rows = [{"id": 1, "score_obtenu": 0.5, "id_aav_cible": 2}]
        cursor = make_cursor_mock(fetchall=rows)
        mock_db.return_value = make_conn_mock(cursor)

        from metric_calculator import get_all_attempts_for_aav
        result = get_all_attempts_for_aav(2)

        assert isinstance(result, list)
        assert isinstance(result[0], dict)


# ==============================================================
# TESTS — count_attempts
# ==============================================================

class TestCountAttempts:

    @patch("metric_calculator.get_db_connection")
    def test_aav_1_six_tentatives(self, mock_db):
        cursor = make_cursor_mock(fetchone=(6,))
        mock_db.return_value = make_conn_mock(cursor)

        from metric_calculator import count_attempts
        assert count_attempts(1) == 6

    @patch("metric_calculator.get_db_connection")
    def test_aav_sans_tentatives_retourne_zero(self, mock_db):
        cursor = make_cursor_mock(fetchone=(0,))
        mock_db.return_value = make_conn_mock(cursor)

        from metric_calculator import count_attempts
        assert count_attempts(7) == 0

    @patch("metric_calculator.get_db_connection")
    def test_aav_2_david_quatre_tentatives(self, mock_db):
        """David a 4 tentatives sur AAV 2 (Char)."""
        cursor = make_cursor_mock(fetchone=(4,))
        mock_db.return_value = make_conn_mock(cursor)

        from metric_calculator import count_attempts
        assert count_attempts(2) == 4


# ==============================================================
# TESTS — count_distinct_learners
# ==============================================================

class TestCountDistinctLearners:

    @patch("metric_calculator.get_db_connection")
    def test_aav_1_quatre_apprenants(self, mock_db):
        """AAV 1 a été tenté par Bob, Charlie, David, Eve → 4 apprenants."""
        cursor = make_cursor_mock(fetchone=(4,))
        mock_db.return_value = make_conn_mock(cursor)

        from metric_calculator import count_distinct_learners
        assert count_distinct_learners(1) == 4

    @patch("metric_calculator.get_db_connection")
    def test_aav_inutilise_zero_apprenants(self, mock_db):
        cursor = make_cursor_mock(fetchone=(0,))
        mock_db.return_value = make_conn_mock(cursor)

        from metric_calculator import count_distinct_learners
        assert count_distinct_learners(17) == 0


# ==============================================================
# TESTS — calculer_couverture
# ==============================================================

class TestCalculerCouverture:

    @patch("metric_calculator.diversity_evaluation_types")
    @patch("metric_calculator.count_prompts")
    @patch("metric_calculator.count_exercices")
    def test_score_complet_0_7(self, mock_ex, mock_pr, mock_div):
        """Exercices + prompts présents, diversité < 3 → 0.4 + 0.3 = 0.7."""
        mock_ex.return_value = 2
        mock_pr.return_value = 1
        mock_div.return_value = 1  # < 3 → pas de bonus

        from metric_calculator import calculer_couverture
        assert calculer_couverture(1) == pytest.approx(0.7)

    @patch("metric_calculator.diversity_evaluation_types")
    @patch("metric_calculator.count_prompts")
    @patch("metric_calculator.count_exercices")
    def test_score_maximal_1_0(self, mock_ex, mock_pr, mock_div):
        """Tout présent + diversité >= 3 → 1.0."""
        mock_ex.return_value = 3
        mock_pr.return_value = 2
        mock_div.return_value = 3

        from metric_calculator import calculer_couverture
        assert calculer_couverture(1) == pytest.approx(1.0)

    @patch("metric_calculator.diversity_evaluation_types")
    @patch("metric_calculator.count_prompts")
    @patch("metric_calculator.count_exercices")
    def test_score_zero_rien(self, mock_ex, mock_pr, mock_div):
        """Rien de présent → 0.0."""
        mock_ex.return_value = 0
        mock_pr.return_value = 0
        mock_div.return_value = 0

        from metric_calculator import calculer_couverture
        assert calculer_couverture(99) == pytest.approx(0.0)

    @patch("metric_calculator.diversity_evaluation_types")
    @patch("metric_calculator.count_prompts")
    @patch("metric_calculator.count_exercices")
    def test_score_exercices_seulement_0_4(self, mock_ex, mock_pr, mock_div):
        """Seulement des exercices → 0.4."""
        mock_ex.return_value = 1
        mock_pr.return_value = 0
        mock_div.return_value = 0

        from metric_calculator import calculer_couverture
        assert calculer_couverture(5) == pytest.approx(0.4)

    @patch("metric_calculator.diversity_evaluation_types")
    @patch("metric_calculator.count_prompts")
    @patch("metric_calculator.count_exercices")
    def test_diversite_exactement_3_ajoute_bonus(self, mock_ex, mock_pr, mock_div):
        """Diversité == 3 (seuil exact) → bonus 0.3 accordé."""
        mock_ex.return_value = 0
        mock_pr.return_value = 0
        mock_div.return_value = 3

        from metric_calculator import calculer_couverture
        assert calculer_couverture(1) == pytest.approx(0.3)


# ==============================================================
# TESTS — calculer_taux_succes
# ==============================================================

class TestCalculerTauxSucces:

    @patch("metric_calculator.get_all_attempts_for_aav")
    def test_aav_sans_tentatives_retourne_zero(self, mock_tentatives):
        mock_tentatives.return_value = []

        from metric_calculator import calculer_taux_succes
        assert calculer_taux_succes(7) == 0.0

    @patch("metric_calculator.get_all_attempts_for_aav")
    def test_aav_une_seule_tentative(self, mock_tentatives):
        """Avec 1 seul score, retourne directement la moyenne (= le score)."""
        mock_tentatives.return_value = [{"score_obtenu": 0.80}]

        from metric_calculator import calculer_taux_succes
        assert calculer_taux_succes(8) == pytest.approx(0.80)

    @patch("metric_calculator.get_all_attempts_for_aav")
    def test_aav_1_moyenne_scores_stables(self, mock_tentatives):
        """AAV 1: scores [0.70, 0.80, 0.85, 0.80, 0.90, 1.00], pas d'outlier."""
        scores = [0.70, 0.80, 0.85, 0.80, 0.90, 1.00]
        mock_tentatives.return_value = [{"score_obtenu": s} for s in scores]

        from metric_calculator import calculer_taux_succes
        result = calculer_taux_succes(1)
        assert result == pytest.approx(sum(scores) / len(scores), abs=0.01)

    @patch("metric_calculator.get_all_attempts_for_aav")
    def test_scores_none_ignores(self, mock_tentatives):
        """Les scores None sont exclus du calcul."""
        mock_tentatives.return_value = [
            {"score_obtenu": 0.80},
            {"score_obtenu": None},
            {"score_obtenu": 0.60},
        ]

        from metric_calculator import calculer_taux_succes
        result = calculer_taux_succes(2)
        assert result == pytest.approx(0.70, abs=0.01)

    @patch("metric_calculator.get_all_attempts_for_aav")
    def test_outlier_filtre_par_3_sigma(self, mock_tentatives):
        """Un score aberrant (outlier > 3σ) est filtré."""
        # scores normaux autour de 0.7, avec un outlier à 10.0
        scores = [0.65, 0.70, 0.75, 0.68, 0.72, 10.0]
        mock_tentatives.return_value = [{"score_obtenu": s} for s in scores]

        from metric_calculator import calculer_taux_succes
        result = calculer_taux_succes(5)
        # Sans l'outlier, la moyenne doit être proche de 0.70
        assert result < 1.0


# ==============================================================
# TESTS — determiner_utilisabilite
# ==============================================================

class TestDeterminerUtilisabilite:

    @patch("metric_calculator.calculer_taux_succes")
    @patch("metric_calculator.calculer_couverture")
    @patch("metric_calculator.get_aav")
    def test_aav_1_utilisable(self, mock_aav, mock_couv, mock_taux):
        """AAV 1: couverture 0.9, taux 0.75, champs présents → utilisable."""
        mock_aav.return_value = {
            "description_markdown": "Comprendre les types entiers",
            "libelle_integration": "les types entiers (int, short, long)"
        }
        mock_couv.return_value = 0.9
        mock_taux.return_value = 0.75

        from metric_calculator import determiner_utilisabilite
        assert determiner_utilisabilite(1) is True

    @patch("metric_calculator.calculer_taux_succes")
    @patch("metric_calculator.calculer_couverture")
    @patch("metric_calculator.get_aav")
    def test_aav_inexistant_non_utilisable(self, mock_aav, mock_couv, mock_taux):
        mock_aav.return_value = None

        from metric_calculator import determiner_utilisabilite
        assert determiner_utilisabilite(999) is False

    @patch("metric_calculator.calculer_taux_succes")
    @patch("metric_calculator.calculer_couverture")
    @patch("metric_calculator.get_aav")
    def test_couverture_insuffisante_non_utilisable(self, mock_aav, mock_couv, mock_taux):
        """couverture 0.5 < 0.7 → non utilisable."""
        mock_aav.return_value = {
            "description_markdown": "desc",
            "libelle_integration": "lib"
        }
        mock_couv.return_value = 0.5
        mock_taux.return_value = 0.75

        from metric_calculator import determiner_utilisabilite
        assert determiner_utilisabilite(6) is False

    @patch("metric_calculator.calculer_taux_succes")
    @patch("metric_calculator.calculer_couverture")
    @patch("metric_calculator.get_aav")
    def test_taux_trop_bas_non_utilisable(self, mock_aav, mock_couv, mock_taux):
        """taux 0.10 <= 0.2 → trop difficile → non utilisable."""
        mock_aav.return_value = {
            "description_markdown": "desc",
            "libelle_integration": "lib"
        }
        mock_couv.return_value = 0.9
        mock_taux.return_value = 0.10

        from metric_calculator import determiner_utilisabilite
        assert determiner_utilisabilite(15) is False

    @patch("metric_calculator.calculer_taux_succes")
    @patch("metric_calculator.calculer_couverture")
    @patch("metric_calculator.get_aav")
    def test_taux_trop_eleve_non_utilisable(self, mock_aav, mock_couv, mock_taux):
        """taux 0.98 >= 0.95 → trop trivial → non utilisable."""
        mock_aav.return_value = {
            "description_markdown": "desc",
            "libelle_integration": "lib"
        }
        mock_couv.return_value = 0.9
        mock_taux.return_value = 0.98

        from metric_calculator import determiner_utilisabilite
        assert determiner_utilisabilite(1) is False

    @patch("metric_calculator.calculer_taux_succes")
    @patch("metric_calculator.calculer_couverture")
    @patch("metric_calculator.get_aav")
    def test_description_manquante_non_utilisable(self, mock_aav, mock_couv, mock_taux):
        """description_markdown vide → non utilisable."""
        mock_aav.return_value = {
            "description_markdown": "",
            "libelle_integration": "lib"
        }
        mock_couv.return_value = 0.9
        mock_taux.return_value = 0.75

        from metric_calculator import determiner_utilisabilite
        assert determiner_utilisabilite(1) is False

    @patch("metric_calculator.calculer_taux_succes")
    @patch("metric_calculator.calculer_couverture")
    @patch("metric_calculator.get_aav")
    def test_libelle_manquant_non_utilisable(self, mock_aav, mock_couv, mock_taux):
        """libelle_integration vide → non utilisable."""
        mock_aav.return_value = {
            "description_markdown": "desc",
            "libelle_integration": ""
        }
        mock_couv.return_value = 0.9
        mock_taux.return_value = 0.75

        from metric_calculator import determiner_utilisabilite
        assert determiner_utilisabilite(1) is False


# ==============================================================
# TESTS — calculer_metriques_aav
# ==============================================================

class TestCalculerMetriquesAAV:

    @patch("metric_calculator.MetriqueQualiteAAVRepository")
    @patch("metric_calculator.get_all_attempts_for_aav")
    @patch("metric_calculator.count_distinct_learners")
    @patch("metric_calculator.count_attempts")
    @patch("metric_calculator.determiner_utilisabilite")
    @patch("metric_calculator.calculer_taux_succes")
    @patch("metric_calculator.calculer_couverture")
    def test_retourne_metrique_aav_1(
        self, mock_couv, mock_taux, mock_util,
        mock_count, mock_learners, mock_tentatives, mock_repo
    ):
        """calculer_metriques_aav agrège correctement toutes les métriques."""
        mock_couv.return_value = 0.9
        mock_taux.return_value = 0.75
        mock_util.return_value = True
        mock_count.return_value = 6
        mock_learners.return_value = 4
        mock_tentatives.return_value = [
            {"score_obtenu": s} for s in [0.70, 0.80, 0.85, 0.80, 0.90, 1.00]
        ]

        fake_metrique = MagicMock()
        fake_metrique.id_aav = 1
        mock_repo.return_value.create.return_value = fake_metrique

        from metric_calculator import calculer_metriques_aav
        result = calculer_metriques_aav(1)

        assert result.id_aav == 1
        mock_repo.return_value.create.assert_called_once()

    @patch("metric_calculator.MetriqueQualiteAAVRepository")
    @patch("metric_calculator.get_all_attempts_for_aav")
    @patch("metric_calculator.count_distinct_learners")
    @patch("metric_calculator.count_attempts")
    @patch("metric_calculator.determiner_utilisabilite")
    @patch("metric_calculator.calculer_taux_succes")
    @patch("metric_calculator.calculer_couverture")
    def test_ecart_type_zero_si_moins_de_deux_scores(
        self, mock_couv, mock_taux, mock_util,
        mock_count, mock_learners, mock_tentatives, mock_repo
    ):
        """Avec 1 seul score, ecart_type_scores doit être 0.0."""
        mock_couv.return_value = 0.7
        mock_taux.return_value = 0.5
        mock_util.return_value = True
        mock_count.return_value = 1
        mock_learners.return_value = 1
        mock_tentatives.return_value = [{"score_obtenu": 0.50}]

        fake_metrique = MagicMock()
        mock_repo.return_value.create.return_value = fake_metrique

        from metric_calculator import calculer_metriques_aav
        calculer_metriques_aav(8)

        call_args = mock_repo.return_value.create.call_args[0][0]
        assert call_args.ecart_type_scores == 0.0


# ==============================================================
# TESTS — get_metriques_by_aav
# ==============================================================

class TestGetMetriquesByAAV:

    @patch("metric_calculator.get_db_connection")
    def test_retourne_dict_aav_1(self, mock_db):
        """Retourne les métriques de l'AAV 1 sous forme de dict."""
        row = {"id_aav": 1, "taux_succes_moyen": 0.75, "est_utilisable": 1}
        cursor = make_cursor_mock(fetchone=row)
        mock_db.return_value = make_conn_mock(cursor)

        from metric_calculator import get_metriques_by_aav
        result = get_metriques_by_aav(1)

        assert result["id_aav"] == 1
        assert result["taux_succes_moyen"] == 0.75

    @patch("metric_calculator.get_db_connection")
    def test_requete_utilise_bon_id(self, mock_db):
        row = {"id_aav": 5}
        cursor = make_cursor_mock(fetchone=row)
        mock_db.return_value = make_conn_mock(cursor)

        from metric_calculator import get_metriques_by_aav
        get_metriques_by_aav(5)

        args = cursor.execute.call_args[0]
        assert args[1] == (5,)


# ==============================================================
# TESTS — get_history
# ==============================================================

class TestGetHistory:

    @patch("metric_calculator.get_db_connection")
    def test_retourne_historique_trie_par_date(self, mock_db):
        rows = [
            {"id_aav": 1, "date_calcul": "2026-02-21"},
            {"id_aav": 1, "date_calcul": "2026-01-15"},
        ]
        cursor = make_cursor_mock(fetchall=rows)
        mock_db.return_value = make_conn_mock(cursor)

        from metric_calculator import get_history
        result = get_history(1)

        assert len(result) == 2
        assert result[0]["date_calcul"] == "2026-02-21"

    @patch("metric_calculator.get_db_connection")
    def test_aucun_historique_retourne_liste_vide(self, mock_db):
        cursor = make_cursor_mock(fetchall=[])
        mock_db.return_value = make_conn_mock(cursor)

        from metric_calculator import get_history
        result = get_history(999)

        assert result == []

    @patch("metric_calculator.get_db_connection")
    def test_retourne_liste_de_dicts(self, mock_db):
        rows = [{"id_aav": 1, "taux_succes_moyen": 0.75}]
        cursor = make_cursor_mock(fetchall=rows)
        mock_db.return_value = make_conn_mock(cursor)

        from metric_calculator import get_history
        result = get_history(1)

        assert isinstance(result, list)
        assert isinstance(result[0], dict)


# ==============================================================
# TESTS — get_all_metrics
# ==============================================================

class TestGetAllMetrics:

    @patch("metric_calculator.get_db_connection")
    def test_retourne_liste(self, mock_db):
        row = (1, 0.9, 0.75, 1, 6, 4, 0.10)
        cursor = make_cursor_mock(fetchone=row)
        mock_db.return_value = make_conn_mock(cursor)

        from metric_calculator import get_all_metrics
        result = get_all_metrics()

        assert isinstance(result, list)

    @patch("metric_calculator.get_db_connection")
    def test_appelle_fetchone(self, mock_db):
        """get_all_metrics utilise fetchone (comportement actuel du code)."""
        cursor = make_cursor_mock(fetchone=(1, 0.9, 0.75))
        mock_db.return_value = make_conn_mock(cursor)

        from metric_calculator import get_all_metrics
        get_all_metrics()

        cursor.fetchone.assert_called_once()