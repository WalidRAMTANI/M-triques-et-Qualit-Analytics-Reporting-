"""
Tests unitaires pour services/metric_calculator.py — Projet PlatonAAV
Données de test basées sur le dump SQL fourni.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


# ==============================================================
# HELPERS
# ==============================================================

def make_session_mock(get_return=None, query_return=None, count_return=None, scalar_return=None, first_return=None):
    session = MagicMock()
    session.__enter__.return_value = session
    session.__exit__.return_value = False
    
    if get_return is not None:
        session.get.return_value = get_return
        
    query = MagicMock()
    session.query.return_value = query
    query.filter.return_value = query
    query.order_by.return_value = query
    query.offset.return_value = query
    query.limit.return_value = query
    
    if query_return is not None:
        query.all.return_value = query_return
    if count_return is not None:
        query.count.return_value = count_return
    if scalar_return is not None:
        query.scalar.return_value = scalar_return
    if first_return is not None:
        query.first.return_value = first_return
        
    return session


# ==============================================================
# TESTS — count_exercices
# ==============================================================

class TestCountExercices:

    @patch("services.metric_calculator.get_db_session")
    def test_aav_1_deux_exercices(self, mock_db):
        """AAV 1 a ids_exercices = [101, 102] → 2."""
        aav = {"id_aav": 1, "ids_exercices": [101, 102]}
        mock_db.return_value = make_session_mock(get_return=aav)

        from services.metric_calculator import count_exercices
        assert count_exercices(1) == 2

    @patch("services.metric_calculator.get_db_session")
    def test_aav_inexistant_retourne_zero(self, mock_db):
        mock_db.return_value = make_session_mock(get_return=None)

        from services.metric_calculator import count_exercices
        assert count_exercices(999) == 0

    @patch("services.metric_calculator.get_db_session")
    def test_ids_exercices_null_retourne_zero(self, mock_db):
        aav = {"id_aav": 5, "ids_exercices": None}
        mock_db.return_value = make_session_mock(get_return=aav)

        from services.metric_calculator import count_exercices
        assert count_exercices(5) == 0


# ==============================================================
# TESTS — count_prompts
# ==============================================================

class TestCountPrompts:

    @patch("services.metric_calculator.get_db_session")
    def test_aav_1_un_prompt(self, mock_db):
        """AAV 1 a prompts_fabrication_ids = [1] → 1."""
        aav = {"id_aav": 1, "prompts_fabrication_ids": [1]}
        mock_db.return_value = make_session_mock(get_return=aav)

        from services.metric_calculator import count_prompts
        assert count_prompts(1) == 1

    @patch("services.metric_calculator.get_db_session")
    def test_aav_inexistant_retourne_zero(self, mock_db):
        mock_db.return_value = make_session_mock(get_return=None)

        from services.metric_calculator import count_prompts
        assert count_prompts(999) == 0


# ==============================================================
# TESTS — diversity_evaluation_types
# ==============================================================

class TestDiversityEvaluationTypes:

    @patch("services.metric_calculator.get_db_session")
    def test_aav_avec_un_type(self, mock_db):
        """AAV 1 a un seul type: 'Calcul Automatisé' → 1."""
        aav = {"id_aav": 1, "type_evaluation": "Calcul Automatisé"}
        mock_db.return_value = make_session_mock(get_return=aav)

        from services.metric_calculator import diversity_evaluation_types
        assert diversity_evaluation_types(1) == 1


# ==============================================================
# TESTS — get_all_attempts_for_aav
# ==============================================================

class TestGetAllAttemptsForAAV:

    @patch("services.metric_calculator.get_db_session")
    def test_aav_1_retourne_six_tentatives(self, mock_db):
        """AAV 1 a 6 tentatives dans le dump."""
        rows = [
            {"id": i, "id_aav_cible": 1, "score_obtenu": s}
            for i, s in enumerate([0.70, 0.80, 0.85, 0.80, 0.90, 1.00], 1)
        ]
        mock_db.return_value = make_session_mock(query_return=rows)

        from services.metric_calculator import get_all_attempts_for_aav
        result = get_all_attempts_for_aav(1)

        assert len(result) == 6
        assert result[0]["score_obtenu"] == 0.70

    @patch("services.metric_calculator.get_db_session")
    def test_aav_sans_tentatives_retourne_liste_vide(self, mock_db):
        mock_db.return_value = make_session_mock(query_return=[])

        from services.metric_calculator import get_all_attempts_for_aav
        assert get_all_attempts_for_aav(7) == []


# ==============================================================
# TESTS — count_attempts
# ==============================================================

class TestCountAttempts:

    @patch("services.metric_calculator.get_db_session")
    def test_aav_1_six_tentatives(self, mock_db):
        mock_db.return_value = make_session_mock(count_return=6)

        from services.metric_calculator import count_attempts
        assert count_attempts(1) == 6


# ==============================================================
# TESTS — count_distinct_learners
# ==============================================================

class TestCountDistinctLearners:

    @patch("services.metric_calculator.get_db_session")
    def test_aav_1_quatre_apprenants(self, mock_db):
        mock_db.return_value = make_session_mock(scalar_return=4)

        from services.metric_calculator import count_distinct_learners
        assert count_distinct_learners(1) == 4


# ==============================================================
# TESTS — calculer_couverture
# ==============================================================

class TestCalculerCouverture:

    @patch("services.metric_calculator.diversity_evaluation_types")
    @patch("services.metric_calculator.count_prompts")
    @patch("services.metric_calculator.count_exercices")
    def test_score_complet_0_7(self, mock_ex, mock_pr, mock_div):
        mock_ex.return_value = 2
        mock_pr.return_value = 1
        mock_div.return_value = 1

        from services.metric_calculator import calculer_couverture
        assert calculer_couverture(1) == pytest.approx(0.7)


# ==============================================================
# TESTS — calculer_taux_succes
# ==============================================================

class TestCalculerTauxSucces:

    @patch("services.metric_calculator.get_all_attempts_for_aav")
    def test_aav_sans_tentatives_retourne_zero(self, mock_tentatives):
        mock_tentatives.return_value = []

        from services.metric_calculator import calculer_taux_succes
        assert calculer_taux_succes(7) == 0.0

    @patch("services.metric_calculator.get_all_attempts_for_aav")
    def test_aav_une_seule_tentative(self, mock_tentatives):
        mock_tentatives.return_value = [{"score_obtenu": 0.80}]

        from services.metric_calculator import calculer_taux_succes
        assert calculer_taux_succes(8) == pytest.approx(0.80)


# ==============================================================
# TESTS — determiner_utilisabilite
# ==============================================================

class TestDeterminerUtilisabilite:

    @patch("services.metric_calculator.calculer_taux_succes")
    @patch("services.metric_calculator.calculer_couverture")
    @patch("services.metric_calculator.get_aav")
    def test_aav_1_utilisable(self, mock_aav, mock_couv, mock_taux):
        mock_aav.return_value = {
            "description_markdown": "Comprendre les types entiers",
            "libelle_integration": "les types entiers (int, short, long)"
        }
        mock_couv.return_value = 0.9
        mock_taux.return_value = 0.75

        from services.metric_calculator import determiner_utilisabilite
        assert determiner_utilisabilite(1) is True


# ==============================================================
# TESTS — calculer_metriques_aav
# ==============================================================

class TestCalculerMetriquesAAV:

    @patch("services.metric_calculator.MetriqueQualiteAAVRepository")
    @patch("services.metric_calculator.get_all_attempts_for_aav")
    @patch("services.metric_calculator.count_distinct_learners")
    @patch("services.metric_calculator.count_attempts")
    @patch("services.metric_calculator.determiner_utilisabilite")
    @patch("services.metric_calculator.calculer_taux_succes")
    @patch("services.metric_calculator.calculer_couverture")
    def test_retourne_metrique_aav_1(
        self, mock_couv, mock_taux, mock_util,
        mock_count, mock_learners, mock_tentatives, mock_repo
    ):
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
        fake_metrique.__getitem__.side_effect = lambda x: getattr(fake_metrique, x)
        mock_repo.return_value.create.return_value = fake_metrique

        from services.metric_calculator import calculer_metriques_aav
        result = calculer_metriques_aav(1)

        assert result["id_aav"] == 1


# ==============================================================
# TESTS — get_metriques_by_aav
# ==============================================================

class TestGetMetriquesByAAV:

    @patch("services.metric_calculator.get_db_session")
    def test_retourne_dict_aav_1(self, mock_db):
        row = {"id_aav": 1, "taux_succes_moyen": 0.75, "est_utilisable": 1}
        mock_db.return_value = make_session_mock(first_return=row)

        from services.metric_calculator import get_metriques_by_aav
        result = get_metriques_by_aav(1)

        assert result["id_aav"] == 1


# ==============================================================
# TESTS — get_history
# ==============================================================

class TestGetHistory:

    @patch("services.metric_calculator.get_db_session")
    def test_retourne_historique_trie_par_date(self, mock_db):
        rows = [
            {"id_aav": 1, "date_calcul": "2026-02-21"},
            {"id_aav": 1, "date_calcul": "2026-01-15"},
        ]
        mock_db.return_value = make_session_mock(query_return=rows)

        from services.metric_calculator import get_history
        result = get_history(1)

        assert len(result) == 2
        assert result[0]["date_calcul"] == "2026-02-21"


# ==============================================================
# TESTS — get_all_metrics
# ==============================================================

class TestGetAllMetrics:

    @patch("services.metric_calculator.get_db_session")
    def test_retourne_liste(self, mock_db):
        row = {"id_aav": 1}
        mock_db.return_value = make_session_mock(query_return=[row])

        from services.metric_calculator import get_all_metrics
        result = get_all_metrics({})

        assert len(result) == 1
        assert result[0]["id_aav"] == 1