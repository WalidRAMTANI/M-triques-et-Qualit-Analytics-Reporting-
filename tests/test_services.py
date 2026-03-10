"""
Tests unitaires pour analytics.py — Projet PlatonAAV
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

# Tentatives par AAV (scores tirés du dump)
TENTATIVES_PAR_AAV = {
    1: [  # Types entiers — scores: 0.70, 0.80, 0.85, 0.80, 0.90, 1.00
        {"score_obtenu": 0.70}, {"score_obtenu": 0.80}, {"score_obtenu": 0.85},
        {"score_obtenu": 0.80}, {"score_obtenu": 0.90}, {"score_obtenu": 1.00},
    ],
    2: [  # Char — scores faibles (David): 0.50, 0.60, 0.20, 0.15, 0.30, 0.25
        {"score_obtenu": 0.50}, {"score_obtenu": 0.60},
        {"score_obtenu": 0.20}, {"score_obtenu": 0.15},
        {"score_obtenu": 0.30}, {"score_obtenu": 0.25},
    ],
    5: [  # Opérateurs — scores: 0.40, 0.45, 0.20, 0.25, 0.15
        {"score_obtenu": 0.40}, {"score_obtenu": 0.45},
        {"score_obtenu": 0.20}, {"score_obtenu": 0.25}, {"score_obtenu": 0.15},
    ],
    6: [  # Comparaison — taux faible: 0.30, 0.10, 0.10
        {"score_obtenu": 0.30}, {"score_obtenu": 0.10}, {"score_obtenu": 0.10},
    ],
    15: [  # Pointeurs — 8 tentatives, taux 0.40
        {"score_obtenu": 0.40}, {"score_obtenu": 0.30}, {"score_obtenu": 0.50},
        {"score_obtenu": 0.20}, {"score_obtenu": 0.60}, {"score_obtenu": 0.40},
        {"score_obtenu": 0.30}, {"score_obtenu": 0.50},
    ],
    # AAVs sans tentatives (inutilisés)
    7: [], 8: [], 9: [], 10: [], 11: [], 12: [], 13: [],
    14: [], 16: [], 17: [], 18: [], 19: [], 20: [],
    3: [], 4: [],
}

# Statuts d'apprentissage (niveau_maitrise) par apprenant
NIVEAUX_MAITRISE = {
    # Alice — aucun statut enregistré → progression 0
    1: [],
    # Bob — 4 statuts
    2: [0.85, 0.60, 0.45, 0.30],
    # Charlie — 14 statuts (mélange maîtrisé/en cours)
    3: [1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 0.90, 0.75, 0.60, 0.50, 0.40, 0.30, 0.20, 0.00],
    # David — 4 statuts avec beaucoup d'échecs
    4: [0.90, 0.25, 0.20, 0.10],
    # Eve — 5 statuts, maîtrise ancienne
    5: [0.95, 0.90, 0.88, 0.85, 0.82],
}

# Nombre d'AAVs non maîtrisés (niveau < 1) par apprenant
AAVS_BLOQUES = {
    1: 0,   # Alice: aucun statut
    2: 4,   # Bob: tous < 1
    3: 8,   # Charlie: AAV 7 à 14 non maîtrisés (0.90, 0.75, ..., 0.00)
    4: 3,   # David: AAV 2,5,6 < 1
    5: 5,   # Eve: tous < 1 (max 0.95)
}


# ==============================================================
# HELPERS pour les mocks
# ==============================================================

def make_db_mock(fetchone_value=None, fetchall_value=None):
    """Crée un mock de connexion DB."""
    cursor = MagicMock()
    cursor.fetchone.return_value = (fetchone_value,) if fetchone_value is not None else (None,)
    cursor.fetchall.return_value = fetchall_value or []
    conn = MagicMock()
    conn.__enter__ = MagicMock(return_value=conn)
    conn.__exit__ = MagicMock(return_value=False)
    conn.cursor.return_value = cursor
    return conn, cursor


# ==============================================================
# TESTS — get_apprenants_ontologie
# ==============================================================

class TestGetApprenantsOntologie:

    @patch("analytics.get_db_connection")
    def test_retourne_apprenants_pour_ontologie_1(self, mock_db):
        conn, cursor = make_db_mock()
        cursor.fetchall.return_value = [
            {"id_apprenant": i, "nom_utilisateur": a["nom_utilisateur"]}
            for i, a in enumerate(APPRENANTS, 1)
        ]
        mock_db.return_value = conn

        from analytics import get_apprenants_ontologie
        result = get_apprenants_ontologie(1)

        assert len(result) == 5
        noms = [r["nom_utilisateur"] for r in result]
        assert "alice_debutante" in noms
        assert "charlie_expert" in noms

    @patch("analytics.get_db_connection")
    def test_ontologie_inexistante_retourne_liste_vide(self, mock_db):
        conn, cursor = make_db_mock()
        cursor.fetchall.return_value = []
        mock_db.return_value = conn

        from analytics import get_apprenants_ontologie
        result = get_apprenants_ontologie(999)

        assert result == []

    @patch("analytics.get_db_connection")
    def test_requete_utilise_bon_id_ontologie(self, mock_db):
        conn, cursor = make_db_mock()
        cursor.fetchall.return_value = []
        mock_db.return_value = conn

        from analytics import get_apprenants_ontologie
        get_apprenants_ontologie(42)

        args = cursor.execute.call_args[0]
        assert args[1] == (42,)


# ==============================================================
# TESTS — count_aavs_bloques
# ==============================================================

class TestCountAAVsBloques:

    @patch("analytics.get_db_connection")
    def test_alice_aucun_aav_bloque(self, mock_db):
        """Alice n'a aucun statut → 0 AAVs bloqués."""
        conn, cursor = make_db_mock(fetchone_value=0)
        mock_db.return_value = conn

        from analytics import count_aavs_bloques
        assert count_aavs_bloques(1) == 0

    @patch("analytics.get_db_connection")
    def test_bob_4_aavs_bloques(self, mock_db):
        """Bob a 4 statuts tous < 1."""
        conn, cursor = make_db_mock(fetchone_value=4)
        mock_db.return_value = conn

        from analytics import count_aavs_bloques
        assert count_aavs_bloques(2) == 4

    @patch("analytics.get_db_connection")
    def test_charlie_8_aavs_bloques(self, mock_db):
        """Charlie a 8 AAVs non encore maîtrisés."""
        conn, cursor = make_db_mock(fetchone_value=8)
        mock_db.return_value = conn

        from analytics import count_aavs_bloques
        assert count_aavs_bloques(3) == 8

    @patch("analytics.get_db_connection")
    def test_filtre_niveau_strictement_inferieur_a_1(self, mock_db):
        """Vérifie que la requête filtre niveau_maitrise < 1."""
        conn, cursor = make_db_mock(fetchone_value=0)
        mock_db.return_value = conn

        from analytics import count_aavs_bloques
        count_aavs_bloques(3)

        sql = cursor.execute.call_args[0][0]
        assert "niveau_maitrise < 1" in sql


# ==============================================================
# TESTS — calculer_progression
# ==============================================================

class TestCalculerProgression:

    @patch("analytics.get_db_connection")
    def test_alice_progression_zero_sans_statuts(self, mock_db):
        """Alice n'a aucun statut → progression 0.0."""
        conn, cursor = make_db_mock(fetchone_value=None)
        cursor.fetchone.return_value = (None,)
        mock_db.return_value = conn

        from analytics import calculer_progression
        assert calculer_progression(1) == 0.0

    @patch("analytics.get_db_connection")
    def test_bob_progression_correcte(self, mock_db):
        """Bob: moyenne de [0.85, 0.60, 0.45, 0.30] ≈ 0.55."""
        expected = sum([0.85, 0.60, 0.45, 0.30]) / 4  # 0.55
        conn, cursor = make_db_mock()
        cursor.fetchone.return_value = (expected,)
        mock_db.return_value = conn

        from analytics import calculer_progression
        result = calculer_progression(2)
        assert abs(result - expected) < 0.01

    @patch("analytics.get_db_connection")
    def test_eve_progression_elevee(self, mock_db):
        """Eve: moyenne de [0.95, 0.90, 0.88, 0.85, 0.82] ≈ 0.88."""
        expected = sum([0.95, 0.90, 0.88, 0.85, 0.82]) / 5
        conn, cursor = make_db_mock()
        cursor.fetchone.return_value = (expected,)
        mock_db.return_value = conn

        from analytics import calculer_progression
        result = calculer_progression(5)
        assert abs(result - expected) < 0.01

    @patch("analytics.get_db_connection")
    def test_retourne_float(self, mock_db):
        conn, cursor = make_db_mock()
        cursor.fetchone.return_value = (0.75,)
        mock_db.return_value = conn

        from analytics import calculer_progression
        result = calculer_progression(3)
        assert isinstance(result, float)

    @patch("analytics.get_db_connection")
    def test_david_progression_faible(self, mock_db):
        """David: moyenne de [0.90, 0.25, 0.20, 0.10] ≈ 0.3625."""
        expected = sum([0.90, 0.25, 0.20, 0.10]) / 4
        conn, cursor = make_db_mock()
        cursor.fetchone.return_value = (expected,)
        mock_db.return_value = conn

        from analytics import calculer_progression
        result = calculer_progression(4)
        assert abs(result - expected) < 0.01


# ==============================================================
# TESTS — detecter_aavs_difficiles
# ==============================================================

class TestDetecterAAVsDifficiles:

    @patch("analytics.count_attempts")
    @patch("analytics.calculer_taux_succes")
    @patch("analytics.get_all_aavs")
    def test_aav_6_comparaison_detecte_difficile(self, mock_aavs, mock_taux, mock_count):
        """AAV 6 (Comparaison) a taux ~0.17 < seuil 0.3."""
        mock_aavs.return_value = [{"id_aav": 6, "nom": "Opérateurs de comparaison"}]
        mock_taux.return_value = 0.17  # (0.30+0.10+0.10)/3
        mock_count.return_value = 3

        from analytics import detecter_aavs_difficiles
        result = detecter_aavs_difficiles(seuil_taux_succes=0.3)

        assert len(result) == 1
        assert result[0].id_aav == 6
        assert result[0].taux_succes == pytest.approx(0.17)

    @patch("analytics.count_attempts")
    @patch("analytics.calculer_taux_succes")
    @patch("analytics.get_all_aavs")
    def test_aav_1_non_detecte_taux_suffisant(self, mock_aavs, mock_taux, mock_count):
        """AAV 1 (Types entiers) a taux 0.75 > seuil 0.3 → non détecté."""
        mock_aavs.return_value = [{"id_aav": 1, "nom": "Types entiers"}]
        mock_taux.return_value = 0.75
        mock_count.return_value = 6

        from analytics import detecter_aavs_difficiles
        result = detecter_aavs_difficiles(seuil_taux_succes=0.3)

        assert result == []

    @patch("analytics.count_attempts")
    @patch("analytics.calculer_taux_succes")
    @patch("analytics.get_all_aavs")
    def test_suggestion_presente(self, mock_aavs, mock_taux, mock_count):
        """Le champ suggestion est bien renseigné."""
        mock_aavs.return_value = [{"id_aav": 15, "nom": "Pointeurs"}]
        mock_taux.return_value = 0.40
        mock_count.return_value = 8

        from analytics import detecter_aavs_difficiles
        result = detecter_aavs_difficiles(seuil_taux_succes=0.5)

        assert len(result) == 1
        assert result[0].suggestion is not None
        assert len(result[0].suggestion) > 0

    @patch("analytics.count_attempts")
    @patch("analytics.calculer_taux_succes")
    @patch("analytics.get_all_aavs")
    def test_seuil_personnalise(self, mock_aavs, mock_taux, mock_count):
        """Avec seuil = 0.6, AAV 5 (taux 0.29) est détecté."""
        mock_aavs.return_value = [{"id_aav": 5, "nom": "Opérateurs arithmétiques"}]
        mock_taux.return_value = 0.29
        mock_count.return_value = 5

        from analytics import detecter_aavs_difficiles
        result = detecter_aavs_difficiles(seuil_taux_succes=0.6)

        assert len(result) == 1
        assert result[0].nb_tentatives == 5

    @patch("analytics.count_attempts")
    @patch("analytics.calculer_taux_succes")
    @patch("analytics.get_all_aavs")
    def test_aucun_aav_difficile(self, mock_aavs, mock_taux, mock_count):
        mock_aavs.return_value = [{"id_aav": 1, "nom": "Types entiers"}]
        mock_taux.return_value = 0.95
        mock_count.return_value = 10

        from analytics import detecter_aavs_difficiles
        assert detecter_aavs_difficiles() == []


# ==============================================================
# TESTS — detecter_apprenants_risque
# ==============================================================

class TestDetecterApprenantsRisque:

    @patch("analytics.count_aavs_bloques")
    @patch("analytics.calculer_progression")
    @patch("analytics.get_apprenants_ontologie")
    def test_alice_detectee_progression_zero(self, mock_apprenants, mock_prog, mock_bloques):
        """Alice a progression 0.0 < seuil 0.1 → détectée à risque."""
        mock_apprenants.return_value = [{"id_apprenant": 1, "nom_utilisateur": "alice_debutante"}]
        mock_prog.return_value = 0.0
        mock_bloques.return_value = 0

        from analytics import detecter_apprenants_risque
        result = detecter_apprenants_risque(id_ontologie=1)

        assert len(result) == 1
        assert result[0].id_apprenant == 1
        assert result[0].nom == "alice_debutante"

    @patch("analytics.count_aavs_bloques")
    @patch("analytics.calculer_progression")
    @patch("analytics.get_apprenants_ontologie")
    def test_charlie_non_detecte_progression_elevee(self, mock_apprenants, mock_prog, mock_bloques):
        """Charlie a progression ~0.62 > seuil 0.1 → non détecté."""
        mock_apprenants.return_value = [{"id_apprenant": 3, "nom_utilisateur": "charlie_expert"}]
        mock_prog.return_value = 0.62
        mock_bloques.return_value = 8

        from analytics import detecter_apprenants_risque
        result = detecter_apprenants_risque(id_ontologie=1)

        assert result == []

    @patch("analytics.count_aavs_bloques")
    @patch("analytics.calculer_progression")
    @patch("analytics.get_apprenants_ontologie")
    def test_aavs_bloques_inclus_dans_resultat(self, mock_apprenants, mock_prog, mock_bloques):
        """Le champ aavs_bloques est correctement renseigné."""
        mock_apprenants.return_value = [{"id_apprenant": 4, "nom_utilisateur": "david_bloque"}]
        mock_prog.return_value = 0.05
        mock_bloques.return_value = 3

        from analytics import detecter_apprenants_risque
        result = detecter_apprenants_risque(id_ontologie=1)

        assert result[0].aavs_bloques == 3

    @patch("analytics.count_aavs_bloques")
    @patch("analytics.calculer_progression")
    @patch("analytics.get_apprenants_ontologie")
    def test_seuil_personnalise(self, mock_apprenants, mock_prog, mock_bloques):
        """Avec seuil 0.6, Bob (progression 0.55) est à risque."""
        mock_apprenants.return_value = [{"id_apprenant": 2, "nom_utilisateur": "bob_progressif"}]
        mock_prog.return_value = 0.55
        mock_bloques.return_value = 4

        from analytics import detecter_apprenants_risque
        result = detecter_apprenants_risque(id_ontologie=1, seuil_avancement=0.6)

        assert len(result) == 1
        assert result[0].progression == pytest.approx(0.55)


# ==============================================================
# TESTS — detecter_aavs_inutilises
# ==============================================================

class TestDetecterAAVsInutilises:

    @patch("analytics.count_attempts")
    @patch("analytics.get_all_aavs")
    def test_aav_sans_tentatives_detecte(self, mock_aavs, mock_count):
        """AAV 7 (Opérateurs logiques) n'a jamais été tenté."""
        mock_aavs.return_value = [{"id_aav": 7, "nom": "Opérateurs logiques"}]
        mock_count.return_value = 0

        from analytics import detecter_aavs_inutilises
        result = detecter_aavs_inutilises()

        assert len(result) == 1
        assert result[0].id_aav == 7
        assert result[0].nom == "Opérateurs logiques"

    @patch("analytics.count_attempts")
    @patch("analytics.get_all_aavs")
    def test_aav_avec_tentatives_non_detecte(self, mock_aavs, mock_count):
        """AAV 1 a 6 tentatives → non inutilisé."""
        mock_aavs.return_value = [{"id_aav": 1, "nom": "Types entiers"}]
        mock_count.return_value = 6

        from analytics import detecter_aavs_inutilises
        result = detecter_aavs_inutilises()

        assert result == []

    @patch("analytics.count_attempts")
    @patch("analytics.get_all_aavs")
    def test_plusieurs_aavs_inutilises(self, mock_aavs, mock_count):
        """Parmi 20 AAVs, ceux sans tentatives sont listés."""
        aavs_sans = [{"id_aav": i, "nom": f"AAV{i}"} for i in [7, 8, 9, 10, 11, 12, 13]]
        aavs_avec = [{"id_aav": 1, "nom": "Types entiers"}]
        mock_aavs.return_value = aavs_sans + aavs_avec
        mock_count.side_effect = lambda id_aav: 0 if id_aav != 1 else 6

        from analytics import detecter_aavs_inutilises
        result = detecter_aavs_inutilises()

        assert len(result) == 7
        ids = [r.id_aav for r in result]
        assert 1 not in ids
        assert 7 in ids

    @patch("analytics.count_attempts")
    @patch("analytics.get_all_aavs")
    def test_liste_vide_si_tous_utilises(self, mock_aavs, mock_count):
        mock_aavs.return_value = [{"id_aav": 1, "nom": "Types entiers"}]
        mock_count.return_value = 10

        from analytics import detecter_aavs_inutilises
        assert detecter_aavs_inutilises() == []


# ==============================================================
# TESTS — detecter_aavs_fragiles
# ==============================================================

class TestDetecterAAVsFragiles:

    @patch("analytics.get_all_attempts_for_aav")
    @patch("analytics.get_all_aavs")
    def test_aav_2_fragile_scores_tres_variables(self, mock_aavs, mock_tentatives):
        """
        AAV 2 (Char): scores [0.50, 0.60, 0.20, 0.15, 0.30, 0.25]
        écart-type ≈ 0.18 > seuil 0.15 → fragile.
        """
        mock_aavs.return_value = [{"id_aav": 2, "nom": "Type caractère"}]
        mock_tentatives.return_value = [
            {"score_obtenu": s} for s in [0.50, 0.60, 0.20, 0.15, 0.30, 0.25]
        ]

        from analytics import detecter_aavs_fragiles
        result = detecter_aavs_fragiles(seuil_ecart_type=0.15)

        assert len(result) == 1
        assert result[0].id_aav == 2

    @patch("analytics.get_all_attempts_for_aav")
    @patch("analytics.get_all_aavs")
    def test_aav_1_stable_non_fragile(self, mock_aavs, mock_tentatives):
        """
        AAV 1 (Types entiers): scores [0.70, 0.80, 0.85, 0.80, 0.90, 1.00]
        écart-type ≈ 0.10 < seuil 0.35 → non fragile.
        """
        mock_aavs.return_value = [{"id_aav": 1, "nom": "Types entiers"}]
        mock_tentatives.return_value = [
            {"score_obtenu": s} for s in [0.70, 0.80, 0.85, 0.80, 0.90, 1.00]
        ]

        from analytics import detecter_aavs_fragiles
        result = detecter_aavs_fragiles(seuil_ecart_type=0.35)

        assert result == []

    @patch("analytics.get_all_attempts_for_aav")
    @patch("analytics.get_all_aavs")
    def test_ignore_aav_moins_de_2_scores(self, mock_aavs, mock_tentatives):
        """Un AAV avec 1 seul score ne peut pas avoir d'écart-type → ignoré."""
        mock_aavs.return_value = [{"id_aav": 8, "nom": "Structure if-else"}]
        mock_tentatives.return_value = [{"score_obtenu": 0.80}]

        from analytics import detecter_aavs_fragiles
        result = detecter_aavs_fragiles()

        assert result == []

    @patch("analytics.get_all_attempts_for_aav")
    @patch("analytics.get_all_aavs")
    def test_ignore_scores_none(self, mock_aavs, mock_tentatives):
        """Les scores None sont filtrés avant le calcul."""
        mock_aavs.return_value = [{"id_aav": 5, "nom": "Opérateurs arithmétiques"}]
        mock_tentatives.return_value = [
            {"score_obtenu": 0.40}, {"score_obtenu": None},
            {"score_obtenu": 0.80}, {"score_obtenu": None},
        ]

        from analytics import detecter_aavs_fragiles
        # Ne doit pas lever d'exception
        result = detecter_aavs_fragiles(seuil_ecart_type=0.15)
        assert isinstance(result, list)

    @patch("analytics.get_all_attempts_for_aav")
    @patch("analytics.get_all_aavs")
    def test_champs_min_max_corrects(self, mock_aavs, mock_tentatives):
        """score_min et score_max sont bien calculés."""
        scores = [0.20, 0.15, 0.30, 0.25, 0.50, 0.60]
        mock_aavs.return_value = [{"id_aav": 2, "nom": "Type caractère"}]
        mock_tentatives.return_value = [{"score_obtenu": s} for s in scores]

        from analytics import detecter_aavs_fragiles
        result = detecter_aavs_fragiles(seuil_ecart_type=0.10)

        assert len(result) == 1
        assert result[0].score_min == pytest.approx(min(scores))
        assert result[0].score_max == pytest.approx(max(scores))

    @patch("analytics.get_all_attempts_for_aav")
    @patch("analytics.get_all_aavs")
    def test_ecart_type_arrondi_4_decimales(self, mock_aavs, mock_tentatives):
        """L'écart-type retourné est arrondi à 4 décimales."""
        mock_aavs.return_value = [{"id_aav": 2, "nom": "Type caractère"}]
        mock_tentatives.return_value = [
            {"score_obtenu": s} for s in [0.20, 0.15, 0.30, 0.25, 0.50, 0.60]
        ]

        from analytics import detecter_aavs_fragiles
        result = detecter_aavs_fragiles(seuil_ecart_type=0.10)

        if result:
            decimales = len(str(result[0].ecart_type_scores).split(".")[-1])
            assert decimales <= 4