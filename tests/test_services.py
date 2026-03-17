"""
Tests unitaires pour alert_detector.py — Projet PlatonAAV
Données de test basées sur le dump SQL fourni.
"""

import pytest
from unittest.mock import patch, MagicMock


# ==============================================================
# HELPERS pour les mocks
# ==============================================================

def make_session_mock(query_return=None, scalar_return=None, count_return=None):
    session = MagicMock()
    session.__enter__.return_value = session
    session.__exit__.return_value = False
    
    query = MagicMock()
    session.query.return_value = query
    query.join.return_value = query
    query.filter.return_value = query
    query.order_by.return_value = query
    
    if query_return is not None:
        query.all.return_value = query_return
    if scalar_return is not None:
        query.scalar.return_value = scalar_return
    if count_return is not None:
        query.count.return_value = count_return
        
    return session


# ==============================================================
# TESTS — get_apprenants_ontologie
# ==============================================================

class TestGetApprenantsOntologie:

    @patch("services.alert_detector.get_db_session")
    def test_retourne_apprenants_pour_ontologie_1(self, mock_db):
        rows = [
            {"id_apprenant": 1, "nom_utilisateur": "alice"},
            {"id_apprenant": 2, "nom_utilisateur": "bob"},
        ]
        mock_db.return_value = make_session_mock(query_return=rows)

        from services.alert_detector import get_apprenants_ontologie
        result = get_apprenants_ontologie(1)

        assert len(result) == 2
        assert result[0]["nom_utilisateur"] == "alice"


# ==============================================================
# TESTS — count_aavs_bloques
# ==============================================================

class TestCountAAVsBloques:

    @patch("services.alert_detector.get_db_session")
    def test_alice_aucun_aav_bloque(self, mock_db):
        mock_db.return_value = make_session_mock(count_return=0)

        from services.alert_detector import count_aavs_bloques
        assert count_aavs_bloques(1) == 0


# ==============================================================
# TESTS — calculer_progression
# ==============================================================

class TestCalculerProgression:

    @patch("services.alert_detector.get_db_session")
    def test_alice_progression_zero_sans_statuts(self, mock_db):
        mock_db.return_value = make_session_mock(scalar_return=0.0)

        from services.alert_detector import calculer_progression
        assert calculer_progression(1) == 0.0


# ==============================================================
# TESTS — detecter_aavs_difficiles
# ==============================================================

class TestDetecterAAVsDifficiles:

    @patch("services.alert_detector.count_attempts")
    @patch("services.alert_detector.calculer_taux_succes")
    @patch("services.alert_detector.get_all_aavs")
    def test_aav_6_comparaison_detecte_difficile(self, mock_aavs, mock_taux, mock_count):
        mock_aavs.return_value = [{"id_aav": 6, "nom": "Opérateurs de comparaison"}]
        mock_taux.return_value = 0.17
        mock_count.return_value = 3

        from services.alert_detector import detecter_aavs_difficiles
        result = detecter_aavs_difficiles(seuil_taux_succes=0.3)

        assert len(result) == 1
        assert result[0].id_aav == 6


# ==============================================================
# TESTS — detecter_apprenants_risque
# ==============================================================

class TestDetecterApprenantsRisque:

    @patch("services.alert_detector.count_aavs_bloques")
    @patch("services.alert_detector.calculer_progression")
    @patch("services.alert_detector.get_apprenants_ontologie")
    def test_alice_detectee_progression_zero(self, mock_apprenants, mock_prog, mock_bloques):
        mock_apprenants.return_value = [{"id_apprenant": 1, "nom_utilisateur": "alice_debutante"}]
        mock_prog.return_value = 0.0
        mock_bloques.return_value = 0

        from services.alert_detector import detecter_apprenants_risque
        result = detecter_apprenants_risque(id_ontologie=1)

        assert len(result) == 1
        assert result[0].id_apprenant == 1


# ==============================================================
# TESTS — detecter_aavs_inutilises
# ==============================================================

class TestDetecterAAVsInutilises:

    @patch("services.alert_detector.count_attempts")
    @patch("services.alert_detector.get_all_aavs")
    def test_aav_sans_tentatives_detecte(self, mock_aavs, mock_count):
        mock_aavs.return_value = [{"id_aav": 7, "nom": "Opérateurs logiques"}]
        mock_count.return_value = 0

        from services.alert_detector import detecter_aavs_inutilises
        result = detecter_aavs_inutilises()

        assert len(result) == 1
        assert result[0].id_aav == 7


# ==============================================================
# TESTS — detecter_aavs_fragiles
# ==============================================================

class TestDetecterAAVsFragiles:

    @patch("services.alert_detector.get_all_attempts_for_aav")
    @patch("services.alert_detector.get_all_aavs")
    def test_aav_2_fragile_scores_tres_variables(self, mock_aavs, mock_tentatives):
        mock_aavs.return_value = [{"id_aav": 2, "nom": "Type caractère"}]
        mock_tentatives.return_value = [
            {"score_obtenu": s} for s in [0.50, 0.60, 0.20, 0.15, 0.30, 0.25]
        ]

        from services.alert_detector import detecter_aavs_fragiles
        result = detecter_aavs_fragiles(seuil_ecart_type=0.15)

        assert len(result) == 1
        assert result[0].id_aav == 2