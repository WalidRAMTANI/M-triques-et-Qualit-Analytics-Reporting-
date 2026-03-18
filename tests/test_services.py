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


def make_session_mock(scalar=None, fetchone=None, fetchall=None):
    """
    Crée un mock de session SQLAlchemy.
    session.execute(...) retourne un résultat dont on peut appeler
    .scalar(), .fetchone() ou .fetchall().
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


# ==============================================================
# TESTS — get_apprenants_ontologie
# ==============================================================

class TestGetApprenantsOntologie:

    @patch("services.alert_detector.get_db_connection")
    def test_retourne_apprenants_pour_ontologie_1(self, mock_db):
        rows = [
            {"id_apprenant": i, "nom_utilisateur": a["nom_utilisateur"]}
            for i, a in enumerate(APPRENANTS, 1)
        ]
        session, result = make_session_mock(fetchall=rows)
        mock_db.return_value = session

        from services.alert_detector import get_apprenants_ontologie
        res = get_apprenants_ontologie(1)

        assert len(res) == 5
        noms = [r["nom_utilisateur"] for r in res]
        assert "alice_debutante" in noms
        assert "charlie_expert" in noms

    @patch("services.alert_detector.get_db_connection")
    def test_ontologie_inexistante_retourne_liste_vide(self, mock_db):
        session, _ = make_session_mock(fetchall=[])
        mock_db.return_value = session

        from services.alert_detector import get_apprenants_ontologie
        assert get_apprenants_ontologie(999) == []

    @patch("services.alert_detector.get_db_connection")
    def test_requete_utilise_bon_id_ontologie(self, mock_db):
        session, _ = make_session_mock(fetchall=[])
        mock_db.return_value = session

        from services.alert_detector import get_apprenants_ontologie
        get_apprenants_ontologie(42)

        call_args = session.execute.call_args
        # Les paramètres nommés SQLAlchemy sont dans le deuxième argument
        assert call_args[0][1]["ontologie_id"] == 42


# ==============================================================
# TESTS — count_aavs_bloques
# ==============================================================

class TestCountAAVsBloques:

    @patch("services.alert_detector.get_db_connection")
    def test_alice_aucun_aav_bloque(self, mock_db):
        session, _ = make_session_mock(scalar=0)
        mock_db.return_value = session

        from services.alert_detector import count_aavs_bloques
        assert count_aavs_bloques(1) == 0

    @patch("services.alert_detector.get_db_connection")
    def test_bob_4_aavs_bloques(self, mock_db):
        session, _ = make_session_mock(scalar=4)
        mock_db.return_value = session

        from services.alert_detector import count_aavs_bloques
        assert count_aavs_bloques(2) == 4

    @patch("services.alert_detector.get_db_connection")
    def test_charlie_8_aavs_bloques(self, mock_db):
        session, _ = make_session_mock(scalar=8)
        mock_db.return_value = session

        from services.alert_detector import count_aavs_bloques
        assert count_aavs_bloques(3) == 8

    @patch("services.alert_detector.get_db_connection")
    def test_filtre_niveau_strictement_inferieur_a_1(self, mock_db):
        session, _ = make_session_mock(scalar=0)
        mock_db.return_value = session

        from services.alert_detector import count_aavs_bloques
        count_aavs_bloques(3)

        sql = str(session.execute.call_args[0][0])
        assert "niveau_maitrise < 1" in sql


# ==============================================================
# TESTS — calculer_progression
# ==============================================================

class TestCalculerProgression:

    @patch("services.alert_detector.get_db_connection")
    def test_alice_progression_zero_sans_statuts(self, mock_db):
        """Alice n'a aucun statut → AVG retourne NULL → 0.0."""
        session, _ = make_session_mock(scalar=None)
        mock_db.return_value = session

        from services.alert_detector import calculer_progression
        assert calculer_progression(1) == 0.0

    @patch("services.alert_detector.get_db_connection")
    def test_bob_progression_correcte(self, mock_db):
        """Bob: [0.85, 0.60, 0.45, 0.30] → moyenne = 0.55."""
        session, _ = make_session_mock(scalar=0.55)
        mock_db.return_value = session

        from services.alert_detector import calculer_progression
        assert abs(calculer_progression(2) - 0.55) < 0.01

    @patch("services.alert_detector.get_db_connection")
    def test_eve_progression_elevee(self, mock_db):
        """Eve: [0.95, 0.90, 0.88, 0.85, 0.82] → moyenne ≈ 0.88."""
        session, _ = make_session_mock(scalar=0.88)
        mock_db.return_value = session

        from services.alert_detector import calculer_progression
        assert abs(calculer_progression(5) - 0.88) < 0.01

    @patch("services.alert_detector.get_db_connection")
    def test_david_progression_faible(self, mock_db):
        """David: [0.90, 0.25, 0.20, 0.10] → moyenne ≈ 0.3625."""
        session, _ = make_session_mock(scalar=0.3625)
        mock_db.return_value = session

        from services.alert_detector import calculer_progression
        assert abs(calculer_progression(4) - 0.3625) < 0.01


# ==============================================================
# TESTS — detecter_apprenants_risque
# ==============================================================

class TestDetecterApprenantsRisque:

    @patch("services.alert_detector.count_aavs_bloques")
    @patch("services.alert_detector.calculer_progression")
    @patch("services.alert_detector.get_apprenants_ontologie")
    def test_david_est_a_risque(self, mock_apprenants, mock_prog, mock_bloques):
        mock_apprenants.return_value = [{"id_apprenant": 4, "nom_utilisateur": "david_bloque"}]
        mock_prog.return_value = 0.05
        mock_bloques.return_value = 3

        from services.alert_detector import detecter_apprenants_risque
        result = detecter_apprenants_risque(id_ontologie=1)

        assert len(result) == 1
        assert result[0].id_apprenant == 4

    @patch("services.alert_detector.count_aavs_bloques")
    @patch("services.alert_detector.calculer_progression")
    @patch("services.alert_detector.get_apprenants_ontologie")
    def test_charlie_non_a_risque(self, mock_apprenants, mock_prog, mock_bloques):
        mock_apprenants.return_value = [{"id_apprenant": 3, "nom_utilisateur": "charlie_expert"}]
        mock_prog.return_value = 0.62
        mock_bloques.return_value = 8

        from services.alert_detector import detecter_apprenants_risque
        result = detecter_apprenants_risque(id_ontologie=1)

        assert result == []

    @patch("services.alert_detector.count_aavs_bloques")
    @patch("services.alert_detector.calculer_progression")
    @patch("services.alert_detector.get_apprenants_ontologie")
    def test_aavs_bloques_inclus_dans_resultat(self, mock_apprenants, mock_prog, mock_bloques):
        mock_apprenants.return_value = [{"id_apprenant": 4, "nom_utilisateur": "david_bloque"}]
        mock_prog.return_value = 0.05
        mock_bloques.return_value = 3

        from services.alert_detector import detecter_apprenants_risque
        result = detecter_apprenants_risque(id_ontologie=1)

        assert result[0].aavs_bloques == 3

    @patch("services.alert_detector.count_aavs_bloques")
    @patch("services.alert_detector.calculer_progression")
    @patch("services.alert_detector.get_apprenants_ontologie")
    def test_seuil_personnalise(self, mock_apprenants, mock_prog, mock_bloques):
        mock_apprenants.return_value = [{"id_apprenant": 2, "nom_utilisateur": "bob_progressif"}]
        mock_prog.return_value = 0.55
        mock_bloques.return_value = 4

        from services.alert_detector import detecter_apprenants_risque
        result = detecter_apprenants_risque(id_ontologie=1, seuil_avancement=0.6)

        assert len(result) == 1
        assert result[0].progression == pytest.approx(0.55)


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
        assert result[0].nom == "Opérateurs logiques"

    @patch("services.alert_detector.count_attempts")
    @patch("services.alert_detector.get_all_aavs")
    def test_aav_avec_tentatives_non_detecte(self, mock_aavs, mock_count):
        mock_aavs.return_value = [{"id_aav": 1, "nom": "Types entiers"}]
        mock_count.return_value = 6

        from services.alert_detector import detecter_aavs_inutilises
        assert detecter_aavs_inutilises() == []

    @patch("services.alert_detector.count_attempts")
    @patch("services.alert_detector.get_all_aavs")
    def test_plusieurs_aavs_inutilises(self, mock_aavs, mock_count):
        aavs_sans = [{"id_aav": i, "nom": f"AAV{i}"} for i in [7, 8, 9, 10, 11, 12, 13]]
        aavs_avec = [{"id_aav": 1, "nom": "Types entiers"}]
        mock_aavs.return_value = aavs_sans + aavs_avec
        mock_count.side_effect = lambda id_aav: 0 if id_aav != 1 else 6

        from services.alert_detector import detecter_aavs_inutilises
        result = detecter_aavs_inutilises()

        assert len(result) == 7
        ids = [r.id_aav for r in result]
        assert 1 not in ids
        assert 7 in ids

    @patch("services.alert_detector.count_attempts")
    @patch("services.alert_detector.get_all_aavs")
    def test_liste_vide_si_tous_utilises(self, mock_aavs, mock_count):
        mock_aavs.return_value = [{"id_aav": 1, "nom": "Types entiers"}]
        mock_count.return_value = 10

        from services.alert_detector import detecter_aavs_inutilises
        assert detecter_aavs_inutilises() == []


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

    @patch("services.alert_detector.get_all_attempts_for_aav")
    @patch("services.alert_detector.get_all_aavs")
    
    def test_aav_1_stable_non_fragile(self, mock_aavs, mock_tentatives):
        mock_aavs.return_value = [{"id_aav": 1, "nom": "Types entiers"}]
        mock_tentatives.return_value = [
            {"score_obtenu": s} for s in [0.70, 0.80, 0.85, 0.80, 0.90, 1.00]
        ]

        from services.alert_detector import detecter_aavs_fragiles
        assert detecter_aavs_fragiles(seuil_ecart_type=0.35) == []

    @patch("services.alert_detector.get_all_attempts_for_aav")
    @patch("services.alert_detector.get_all_aavs")
    def test_ignore_aav_moins_de_2_scores(self, mock_aavs, mock_tentatives):
        mock_aavs.return_value = [{"id_aav": 8, "nom": "Structure if-else"}]
        mock_tentatives.return_value = [{"score_obtenu": 0.80}]

        from services.alert_detector import detecter_aavs_fragiles
        assert detecter_aavs_fragiles() == []

    @patch("services.alert_detector.get_all_attempts_for_aav")
    @patch("services.alert_detector.get_all_aavs")
    def test_ignore_scores_none(self, mock_aavs, mock_tentatives):
        mock_aavs.return_value = [{"id_aav": 5, "nom": "Opérateurs arithmétiques"}]
        mock_tentatives.return_value = [
            {"score_obtenu": 0.40}, {"score_obtenu": None},
            {"score_obtenu": 0.80}, {"score_obtenu": None},
        ]

        from services.alert_detector import detecter_aavs_fragiles
        result = detecter_aavs_fragiles(seuil_ecart_type=0.15)
        assert isinstance(result, list)

    @patch("services.alert_detector.get_all_attempts_for_aav")
    @patch("services.alert_detector.get_all_aavs")
    def test_champs_min_max_corrects(self, mock_aavs, mock_tentatives):
        scores = [0.20, 0.15, 0.30, 0.25, 0.50, 0.60]
        mock_aavs.return_value = [{"id_aav": 2, "nom": "Type caractère"}]
        mock_tentatives.return_value = [{"score_obtenu": s} for s in scores]

        from services.alert_detector import detecter_aavs_fragiles
        result = detecter_aavs_fragiles(seuil_ecart_type=0.10)

        assert len(result) == 1
        assert result[0].score_min == pytest.approx(min(scores))
        assert result[0].score_max == pytest.approx(max(scores))

    @patch("services.alert_detector.get_all_attempts_for_aav")
    @patch("services.alert_detector.get_all_aavs")
    def test_ecart_type_arrondi_4_decimales(self, mock_aavs, mock_tentatives):
        mock_aavs.return_value = [{"id_aav": 2, "nom": "Type caractère"}]
        mock_tentatives.return_value = [
            {"score_obtenu": s} for s in [0.20, 0.15, 0.30, 0.25, 0.50, 0.60]
        ]

        from services.alert_detector import detecter_aavs_fragiles
        result = detecter_aavs_fragiles(seuil_ecart_type=0.10)

        if result:
            decimales = len(str(result[0].ecart_type_scores).split(".")[-1])
            assert decimales <= 4