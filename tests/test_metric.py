"""
Tests unitaires pour services/metric_calculator.py — Projet PlatonAAV
Données de test basées sur le dump SQL fourni.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


# ==============================================================
# HELPERS — interface SQLAlchemy ORM
# ==============================================================

def make_model_mock(data: dict):
    """Crée un mock d'objet modèle SQLAlchemy (pour .query().filter().first())."""
    model = MagicMock()
    for key, value in data.items():
        setattr(model, key, value)
    return model


def make_query_mock(scalar=None, first=None, all=None):
    """
    Crée un mock de session.query() pour SQLAlchemy ORM.
    Supporte chaîning: .query(...).filter(...).scalar() / .first() / .all()
    """
    # Le result de query()
    query_result = MagicMock()
    query_result.scalar.return_value = scalar
    query_result.first.return_value = first
    query_result.all.return_value = all if all is not None else []
    
    # filter() retourne la même chose (pour le chaîning)
    query_result.filter.return_value = query_result
    query_result.join.return_value = query_result
    query_result.outerjoin.return_value = query_result
    query_result.order_by.return_value = query_result
    
    # query() retourne query_result
    session = MagicMock()
    session.__enter__ = MagicMock(return_value=session)
    session.__exit__ = MagicMock(return_value=False)
    session.query.return_value = query_result
    
    return session, query_result


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


# ==============================================================
# TESTS — count_exercices
# ==============================================================

class TestCountExercices:

    @patch("services.metric_calculator.from_json")
    @patch("services.metric_calculator.get_db_connection")
    def test_aav_1_deux_exercices(self, mock_db, mock_json):
        session, _ = make_session_mock(first={"ids_exercices": "[101, 102]"})
        mock_db.return_value = session
        mock_json.return_value = [101, 102]

        from services.metric_calculator import count_exercices
        assert count_exercices(1) == 2

    @patch("services.metric_calculator.from_json")
    @patch("services.metric_calculator.get_db_connection")
    def test_aav_inexistant_retourne_zero(self, mock_db, mock_json):
        session, result = make_session_mock()
        result.fetchone.return_value = None
        mock_db.return_value = session

        from services.metric_calculator import count_exercices
        assert count_exercices(999) == 0

    @patch("services.metric_calculator.from_json")
    @patch("services.metric_calculator.get_db_connection")
    def test_ids_exercices_null_retourne_zero(self, mock_db, mock_json):
        session, _ = make_session_mock(first={"ids_exercices": None})
        mock_db.return_value = session

        from services.metric_calculator import count_exercices
        assert count_exercices(5) == 0

    @patch("services.metric_calculator.from_json")
    @patch("services.metric_calculator.get_db_connection")
    def test_aav_composite_19_six_exercices(self, mock_db, mock_json):
        session, _ = make_session_mock(first={"ids_exercices": "[101,102,103,104,105,106]"})
        mock_db.return_value = session
        mock_json.return_value = [101, 102, 103, 104, 105, 106]

        from services.metric_calculator import count_exercices
        assert count_exercices(19) == 6


# ==============================================================
# TESTS — count_prompts
# ==============================================================

class TestCountPrompts:

    @patch("services.metric_calculator.from_json")
    @patch("services.metric_calculator.get_db_connection")
    def test_aav_1_un_prompt(self, mock_db, mock_json):
        session, _ = make_session_mock(first={"prompts_fabrication_ids": "[1]"})
        mock_db.return_value = session
        mock_json.return_value = [1]

        from services.metric_calculator import count_prompts
        assert count_prompts(1) == 1

    @patch("services.metric_calculator.from_json")
    @patch("services.metric_calculator.get_db_connection")
    def test_aav_inexistant_retourne_zero(self, mock_db, mock_json):
        session, result = make_session_mock()
        result.fetchone.return_value = None
        mock_db.return_value = session

        from services.metric_calculator import count_prompts
        assert count_prompts(999) == 0

    @patch("services.metric_calculator.from_json")
    @patch("services.metric_calculator.get_db_connection")
    def test_prompts_null_retourne_zero(self, mock_db, mock_json):
        session, _ = make_session_mock(first={"prompts_fabrication_ids": None})
        mock_db.return_value = session

        from services.metric_calculator import count_prompts
        assert count_prompts(3) == 0

    @patch("services.metric_calculator.from_json")
    @patch("services.metric_calculator.get_db_connection")
    def test_aav_19_trois_prompts(self, mock_db, mock_json):
        session, _ = make_session_mock(first={"prompts_fabrication_ids": "[1, 2, 3]"})
        mock_db.return_value = session
        mock_json.return_value = [1, 2, 3]

        from services.metric_calculator import count_prompts
        assert count_prompts(19) == 3


# ==============================================================
# TESTS — diversity_evaluation_types
# ==============================================================

class TestDiversityEvaluationTypes:

    @patch("services.metric_calculator.get_db_connection")
    def test_aav_avec_un_type(self, mock_db):
        session, _ = make_session_mock(scalar=1)
        mock_db.return_value = session

        from services.metric_calculator import diversity_evaluation_types
        assert diversity_evaluation_types(1) == 1

    @patch("services.metric_calculator.get_db_connection")
    def test_retourne_entier(self, mock_db):
        session, _ = make_session_mock(scalar=2)
        mock_db.return_value = session

        from services.metric_calculator import diversity_evaluation_types
        result = diversity_evaluation_types(8)
        assert isinstance(result, int)


# ==============================================================
# TESTS — get_all_attempts_for_aav
# ==============================================================

class TestGetAllAttemptsForAAV:

    @patch("services.metric_calculator.get_db_connection")
    def test_aav_1_retourne_six_tentatives(self, mock_db):
        rows = [
            {"id": i, "id_aav_cible": 1, "score_obtenu": s}
            for i, s in enumerate([0.70, 0.80, 0.85, 0.80, 0.90, 1.00], 1)
        ]
        session, _ = make_session_mock(all_results=rows)
        mock_db.return_value = session

        from services.metric_calculator import get_all_attempts_for_aav
        result = get_all_attempts_for_aav(1)

        assert len(result) == 6
        assert result[0]["score_obtenu"] == 0.70

    @patch("services.metric_calculator.get_db_connection")
    def test_aav_sans_tentatives_retourne_liste_vide(self, mock_db):
        session, _ = make_session_mock(all_results=[])
        mock_db.return_value = session

        from services.metric_calculator import get_all_attempts_for_aav
        assert get_all_attempts_for_aav(7) == []

    @patch("services.metric_calculator.get_db_connection")
    def test_retourne_liste_de_dicts(self, mock_db):
        rows = [{"id": 1, "score_obtenu": 0.5, "id_aav_cible": 2}]
        session, _ = make_session_mock(all_results=rows)
        mock_db.return_value = session

        from services.metric_calculator import get_all_attempts_for_aav
        result = get_all_attempts_for_aav(2)

        assert isinstance(result, list)
        assert isinstance(result[0], dict)


# ==============================================================
# TESTS — count_attempts
# ==============================================================

class TestCountAttempts:

    @patch("services.metric_calculator.get_db_connection")
    def test_aav_1_six_tentatives(self, mock_db):
        session, _ = make_session_mock(scalar=6)
        mock_db.return_value = session

        from services.metric_calculator import count_attempts
        assert count_attempts(1) == 6

    @patch("services.metric_calculator.get_db_connection")
    def test_aav_sans_tentatives_retourne_zero(self, mock_db):
        session, _ = make_session_mock(scalar=0)
        mock_db.return_value = session

        from services.metric_calculator import count_attempts
        assert count_attempts(7) == 0

    @patch("services.metric_calculator.get_db_connection")
    def test_aav_2_david_quatre_tentatives(self, mock_db):
        session, _ = make_session_mock(scalar=4)
        mock_db.return_value = session

        from services.metric_calculator import count_attempts
        assert count_attempts(2) == 4


# ==============================================================
# TESTS — count_distinct_learners
# ==============================================================

class TestCountDistinctLearners:

    @patch("services.metric_calculator.get_db_connection")
    def test_aav_1_quatre_apprenants(self, mock_db):
        session, _ = make_session_mock(scalar=4)
        mock_db.return_value = session

        from services.metric_calculator import count_distinct_learners
        assert count_distinct_learners(1) == 4

    @patch("services.metric_calculator.get_db_connection")
    def test_aav_inutilise_zero_apprenants(self, mock_db):
        session, _ = make_session_mock(scalar=0)
        mock_db.return_value = session

        from services.metric_calculator import count_distinct_learners
        assert count_distinct_learners(17) == 0


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

    @patch("services.metric_calculator.diversity_evaluation_types")
    @patch("services.metric_calculator.count_prompts")
    @patch("services.metric_calculator.count_exercices")
    def test_score_maximal_1_0(self, mock_ex, mock_pr, mock_div):
        mock_ex.return_value = 3
        mock_pr.return_value = 2
        mock_div.return_value = 3

        from services.metric_calculator import calculer_couverture
        assert calculer_couverture(1) == pytest.approx(1.0)

    @patch("services.metric_calculator.diversity_evaluation_types")
    @patch("services.metric_calculator.count_prompts")
    @patch("services.metric_calculator.count_exercices")
    def test_score_zero_rien(self, mock_ex, mock_pr, mock_div):
        mock_ex.return_value = 0
        mock_pr.return_value = 0
        mock_div.return_value = 0

        from services.metric_calculator import calculer_couverture
        assert calculer_couverture(99) == pytest.approx(0.0)

    @patch("services.metric_calculator.diversity_evaluation_types")
    @patch("services.metric_calculator.count_prompts")
    @patch("services.metric_calculator.count_exercices")
    def test_score_exercices_seulement_0_4(self, mock_ex, mock_pr, mock_div):
        mock_ex.return_value = 1
        mock_pr.return_value = 0
        mock_div.return_value = 0

        from services.metric_calculator import calculer_couverture
        assert calculer_couverture(5) == pytest.approx(0.4)

    @patch("services.metric_calculator.diversity_evaluation_types")
    @patch("services.metric_calculator.count_prompts")
    @patch("services.metric_calculator.count_exercices")
    def test_diversite_exactement_3_ajoute_bonus(self, mock_ex, mock_pr, mock_div):
        mock_ex.return_value = 0
        mock_pr.return_value = 0
        mock_div.return_value = 3

        from services.metric_calculator import calculer_couverture
        assert calculer_couverture(1) == pytest.approx(0.3)


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

    @patch("services.metric_calculator.get_all_attempts_for_aav")
    def test_aav_1_moyenne_scores_stables(self, mock_tentatives):
        scores = [0.70, 0.80, 0.85, 0.80, 0.90, 1.00]
        mock_tentatives.return_value = [{"score_obtenu": s} for s in scores]

        from services.metric_calculator import calculer_taux_succes
        result = calculer_taux_succes(1)
        assert result == pytest.approx(sum(scores) / len(scores), abs=0.01)

    @patch("services.metric_calculator.get_all_attempts_for_aav")
    def test_scores_none_ignores(self, mock_tentatives):
        mock_tentatives.return_value = [
            {"score_obtenu": 0.80},
            {"score_obtenu": None},
            {"score_obtenu": 0.60},
        ]

        from services.metric_calculator import calculer_taux_succes
        result = calculer_taux_succes(2)
        assert result == pytest.approx(0.70, abs=0.01)

    @patch("services.metric_calculator.get_all_attempts_for_aav")
    def test_outlier_filtre_par_3_sigma(self, mock_tentatives):
        scores = [0.70] * 30 + [100.0]
        mock_tentatives.return_value = [{"score_obtenu": s} for s in scores]

        from services.metric_calculator import calculer_taux_succes
        result = calculer_taux_succes(5)
        assert result < 1.0


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

    @patch("services.metric_calculator.calculer_taux_succes")
    @patch("services.metric_calculator.calculer_couverture")
    @patch("services.metric_calculator.get_aav")
    def test_aav_inexistant_non_utilisable(self, mock_aav, mock_couv, mock_taux):
        mock_aav.return_value = None

        from services.metric_calculator import determiner_utilisabilite
        assert determiner_utilisabilite(999) is False

    @patch("services.metric_calculator.calculer_taux_succes")
    @patch("services.metric_calculator.calculer_couverture")
    @patch("services.metric_calculator.get_aav")
    def test_couverture_insuffisante_non_utilisable(self, mock_aav, mock_couv, mock_taux):
        mock_aav.return_value = {"description_markdown": "desc", "libelle_integration": "lib"}
        mock_couv.return_value = 0.5
        mock_taux.return_value = 0.75

        from services.metric_calculator import determiner_utilisabilite
        assert determiner_utilisabilite(6) is False

    @patch("services.metric_calculator.calculer_taux_succes")
    @patch("services.metric_calculator.calculer_couverture")
    @patch("services.metric_calculator.get_aav")
    def test_taux_trop_bas_non_utilisable(self, mock_aav, mock_couv, mock_taux):
        mock_aav.return_value = {"description_markdown": "desc", "libelle_integration": "lib"}
        mock_couv.return_value = 0.9
        mock_taux.return_value = 0.10

        from services.metric_calculator import determiner_utilisabilite
        assert determiner_utilisabilite(15) is False

    @patch("services.metric_calculator.calculer_taux_succes")
    @patch("services.metric_calculator.calculer_couverture")
    @patch("services.metric_calculator.get_aav")
    def test_taux_trop_eleve_non_utilisable(self, mock_aav, mock_couv, mock_taux):
        mock_aav.return_value = {"description_markdown": "desc", "libelle_integration": "lib"}
        mock_couv.return_value = 0.9
        mock_taux.return_value = 0.98

        from services.metric_calculator import determiner_utilisabilite
        assert determiner_utilisabilite(1) is False

    @patch("services.metric_calculator.calculer_taux_succes")
    @patch("services.metric_calculator.calculer_couverture")
    @patch("services.metric_calculator.get_aav")
    def test_description_manquante_non_utilisable(self, mock_aav, mock_couv, mock_taux):
        mock_aav.return_value = {"description_markdown": "", "libelle_integration": "lib"}
        mock_couv.return_value = 0.9
        mock_taux.return_value = 0.75

        from services.metric_calculator import determiner_utilisabilite
        assert determiner_utilisabilite(1) is False

    @patch("services.metric_calculator.calculer_taux_succes")
    @patch("services.metric_calculator.calculer_couverture")
    @patch("services.metric_calculator.get_aav")
    def test_libelle_manquant_non_utilisable(self, mock_aav, mock_couv, mock_taux):
        mock_aav.return_value = {"description_markdown": "desc", "libelle_integration": ""}
        mock_couv.return_value = 0.9
        mock_taux.return_value = 0.75

        from services.metric_calculator import determiner_utilisabilite
        assert determiner_utilisabilite(1) is False


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
        mock_repo.return_value.create.return_value = fake_metrique

        from services.metric_calculator import calculer_metriques_aav
        result = calculer_metriques_aav(1)

        assert result.id_aav == 1
        mock_repo.return_value.create.assert_called_once()

    @patch("services.metric_calculator.MetriqueQualiteAAVRepository")
    @patch("services.metric_calculator.get_all_attempts_for_aav")
    @patch("services.metric_calculator.count_distinct_learners")
    @patch("services.metric_calculator.count_attempts")
    @patch("services.metric_calculator.determiner_utilisabilite")
    @patch("services.metric_calculator.calculer_taux_succes")
    @patch("services.metric_calculator.calculer_couverture")
    def test_ecart_type_zero_si_moins_de_deux_scores(
        self, mock_couv, mock_taux, mock_util,
        mock_count, mock_learners, mock_tentatives, mock_repo
    ):
        mock_couv.return_value = 0.7
        mock_taux.return_value = 0.5
        mock_util.return_value = True
        mock_count.return_value = 1
        mock_learners.return_value = 1
        mock_tentatives.return_value = [{"score_obtenu": 0.50}]

        fake_metrique = MagicMock()
        mock_repo.return_value.create.return_value = fake_metrique

        from services.metric_calculator import calculer_metriques_aav
        calculer_metriques_aav(8)

        call_args = mock_repo.return_value.create.call_args[0][0]
        assert call_args.ecart_type_scores == 0.0


# ==============================================================
# TESTS — get_metriques_by_aav
# ==============================================================

class TestGetMetriquesByAAV:

    @patch("services.metric_calculator.get_db_connection")
    def test_retourne_dict_aav_1(self, mock_db):
        session, _ = make_session_mock(first={"id_aav": 1, "taux_succes_moyen": 0.75, "est_utilisable": 1})
        mock_db.return_value = session

        from services.metric_calculator import get_metriques_by_aav
        result = get_metriques_by_aav(1)

        assert result["id_aav"] == 1
        assert result["taux_succes_moyen"] == 0.75


# ==============================================================
# TESTS — get_history
# ==============================================================

class TestGetHistory:

    @patch("services.metric_calculator.get_db_connection")
    def test_retourne_historique_trie_par_date(self, mock_db):
        rows = [
            {"id_aav": 1, "date_calcul": "2026-02-21"},
            {"id_aav": 1, "date_calcul": "2026-01-15"},
        ]
        session, _ = make_session_mock(all_results=rows)
        mock_db.return_value = session

        from services.metric_calculator import get_history
        result = get_history(1)

        assert len(result) == 2
        assert result[0]["date_calcul"] == "2026-02-21"

    @patch("services.metric_calculator.get_db_connection")
    def test_aucun_historique_retourne_liste_vide(self, mock_db):
        session, _ = make_session_mock(all_results=[])
        mock_db.return_value = session

        from services.metric_calculator import get_history
        assert get_history(999) == []

    @patch("services.metric_calculator.get_db_connection")
    def test_retourne_liste_de_dicts(self, mock_db):
        rows = [{"id_aav": 1, "taux_succes_moyen": 0.75}]
        session, _ = make_session_mock(all_results=rows)
        mock_db.return_value = session

        from services.metric_calculator import get_history
        result = get_history(1)

        assert isinstance(result, list)
        assert isinstance(result[0], dict)


# ==============================================================
# TESTS — get_all_metrics
# ==============================================================

class TestGetAllMetrics:

    @patch("services.metric_calculator.get_db_connection")
    def test_retourne_liste(self, mock_db):
        row = {
            "id_metrique": 1,
            "id_aav": 1,
            "score_covering_ressources": 0.9,
            "taux_succes_moyen": 0.75,
            "est_utilisable": True,
            "nb_tentatives_total": 10,
            "nb_apprenants_distincts": 5,
            "ecart_type_scores": 0.1,
            "date_calcul": datetime.now(),
            "periode_debut": datetime.now(),
            "periode_fin": datetime.now()
        }
        session, _ = make_session_mock(all_results=[row])
        mock_db.return_value = session

        from services.metric_calculator import get_all_metrics
        result = get_all_metrics({})

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].id_aav == 1