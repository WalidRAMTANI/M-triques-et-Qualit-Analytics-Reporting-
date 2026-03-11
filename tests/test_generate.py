"""
Tests unitaires pour services/report_generator.py — Projet PlatonAAV
Données de test basées sur le dump SQL fourni.
"""

import pytest
from datetime import datetime
import base64
from unittest.mock import patch, MagicMock


# ==============================================================
# DONNÉES DE TEST (issues du dump SQL)
# ==============================================================

AAV_1 = {
    "id_aav": 1,
    "nom": "Types entiers",
    "discipline": "Programmation",
    "description_markdown": "Comprendre et utiliser les types entiers en C",
    "libelle_integration": "les types entiers (int, short, long)"
}

AAV_5 = {
    "id_aav": 5,
    "nom": "Opérateurs arithmétiques",
    "discipline": "Programmation",
    "description_markdown": "Utiliser les opérateurs arithmétiques",
    "libelle_integration": "les opérateurs arithmétiques (+, -, *, /, %)"
}

STUDENT_BOB = {
    "id_apprenant": 2,
    "nom": "bob_progressif",
    "email": "bob@example.com",
    "date_inscription": "2026-01-10 09:00:00",
    "derniere_connexion": "2026-02-21 10:15:00"
}

TENTATIVES_BOB = [
    {"id_aav": 1, "nom": "Types entiers",         "score_obtenu": 0.85, "date_tentative": "2026-02-20"},
    {"id_aav": 2, "nom": "Type caractère",         "score_obtenu": 0.60, "date_tentative": "2026-02-19"},
    {"id_aav": 5, "nom": "Opérateurs arithmétiques","score_obtenu": 0.45, "date_tentative": "2026-02-18"},
]


# ==============================================================
# HELPERS
# ==============================================================

def make_conn_mock(fetchone=None, fetchall=None):
    cursor = MagicMock()
    cursor.fetchone.return_value = fetchone
    cursor.fetchall.return_value = fetchall or []
    conn = MagicMock()
    conn.__enter__ = MagicMock(return_value=conn)
    conn.__exit__ = MagicMock(return_value=False)
    conn.cursor.return_value = cursor
    return conn, cursor


# ==============================================================
# TESTS — generate_csv_string
# ==============================================================

class TestGenerateCsvString:

    def test_dict_unique_produit_csv(self):
        from services.report_generator import generate_csv_string
        fields = ["id_aav", "nom", "taux_succes"]
        data = {"id_aav": 1, "nom": "Types entiers", "taux_succes": 0.75}
        result = generate_csv_string(data, fields)

        assert "id_aav" in result
        assert "Types entiers" in result
        assert "0.75" in result

    def test_liste_de_dicts_produit_plusieurs_lignes(self):
        from services.report_generator import generate_csv_string
        fields = ["id_aav", "nom"]
        data = [
            {"id_aav": 1, "nom": "Types entiers"},
            {"id_aav": 5, "nom": "Opérateurs arithmétiques"},
        ]
        result = generate_csv_string(data, fields)
        lines = [l for l in result.strip().split("\n") if l]

        assert len(lines) == 3  # header + 2 lignes
        assert "Types entiers" in result

    def test_liste_simple_zippee_avec_fieldnames(self):
        """Une liste plate [1, 'Maths', 80] est zippée avec les fieldnames."""
        from services.report_generator import generate_csv_string
        fields = ["id", "nom", "score"]
        data = [1, "Maths", 80]
        result = generate_csv_string(data, fields)

        assert "id" in result
        assert "Maths" in result

    def test_header_present_en_premiere_ligne(self):
        from services.report_generator import generate_csv_string
        fields = ["id_aav", "nom"]
        data = [{"id_aav": 1, "nom": "Types entiers"}]
        result = generate_csv_string(data, fields)
        first_line = result.split("\n")[0]

        assert "id_aav" in first_line
        assert "nom" in first_line

    def test_retourne_string(self):
        from services.report_generator import generate_csv_string
        result = generate_csv_string({"a": 1}, ["a"])
        assert isinstance(result, str)


# ==============================================================
# TESTS — to_pdf
# ==============================================================

class TestToPdf:

    def test_retourne_string_base64_valide(self):
        from services.report_generator import to_pdf
        result = to_pdf({"id_aav": 1, "nom": "Types entiers"}, title="Test")
        decoded = base64.b64decode(result)
        assert decoded[:4] == b"%PDF"

    def test_titre_encode_dans_pdf(self):
        from services.report_generator import to_pdf
        result = to_pdf({"cle": "valeur"}, title="MonTitre")
        decoded = base64.b64decode(result).decode("ascii", errors="ignore")
        assert "MonTitre" in decoded

    def test_accents_supprimes_sans_crash(self):
        """Les caractères non-ASCII sont ignorés (encode ascii ignore)."""
        from services.report_generator import to_pdf
        result = to_pdf({"nom": "Opérateurs"}, title="Rapport")
        assert isinstance(result, str)

    def test_parentheses_echappees(self):
        """Les parenthèses dans les données ne doivent pas corrompre le PDF."""
        from services.report_generator import to_pdf
        result = to_pdf({"note": "résultat (excellent)"}, title="Test")
        decoded = base64.b64decode(result).decode("ascii", errors="ignore")
        assert "\\(" in decoded or "excellent" in decoded

    def test_retourne_string(self):
        from services.report_generator import to_pdf
        result = to_pdf({})
        assert isinstance(result, str)


# ==============================================================
# TESTS — get_student
# ==============================================================

class TestGetStudent:

    @patch("services.report_generator.get_db_connection")
    def test_bob_retourne_dict_correct(self, mock_db):
        row = MagicMock()
        row.__getitem__ = lambda self, k: {
            "id_apprenant": 2,
            "nom_utilisateur": "bob_progressif",
            "email": "bob@example.com",
            "date_inscription": "2026-01-10",
            "derniere_connexion": "2026-02-21"
        }[k]
        conn, cursor = make_conn_mock(fetchone=row)
        mock_db.return_value = conn

        from services.report_generator import get_student
        result = get_student(2)

        assert result["id_apprenant"] == 2
        assert result["nom"] == "bob_progressif"
        assert result["email"] == "bob@example.com"

    @patch("services.report_generator.get_db_connection")
    def test_apprenant_inexistant_retourne_none(self, mock_db):
        conn, cursor = make_conn_mock(fetchone=None)
        mock_db.return_value = conn

        from services.report_generator import get_student
        assert get_student(999) is None

    @patch("services.report_generator.get_db_connection")
    def test_requete_utilise_bon_id(self, mock_db):
        conn, cursor = make_conn_mock(fetchone=None)
        mock_db.return_value = conn

        from services.report_generator import get_student
        get_student(42)

        args = cursor.execute.call_args[0]
        assert args[1] == (42,)


# ==============================================================
# TESTS — collect_data_for_aav
# ==============================================================

class TestCollectDataForAAV:

    def _patch_metrics(self, mock_aav, mock_taux, mock_couv, mock_util, mock_count, mock_learners):
        mock_aav.return_value = AAV_1
        mock_taux.return_value = 0.75
        mock_couv.return_value = 0.9
        mock_util.return_value = True
        mock_count.return_value = 6
        mock_learners.return_value = 4

    @patch("services.report_generator.count_distinct_learners")
    @patch("services.report_generator.count_attempts")
    @patch("services.report_generator.determiner_utilisabilite")
    @patch("services.report_generator.calculer_couverture")
    @patch("services.report_generator.calculer_taux_succes")
    @patch("services.report_generator.get_aav")
    def test_format_json_retourne_dict(self, mock_aav, mock_taux, mock_couv, mock_util, mock_count, mock_learners):
        self._patch_metrics(mock_aav, mock_taux, mock_couv, mock_util, mock_count, mock_learners)

        from services.report_generator import collect_data_for_aav
        result = collect_data_for_aav(1, "json")

        assert isinstance(result, dict)
        assert result["id_aav"] == 1
        assert result["nom"] == "Types entiers"
        assert result["taux_succes"] == 0.75
        assert result["nb_tentatives"] == 6

    @patch("services.report_generator.count_distinct_learners")
    @patch("services.report_generator.count_attempts")
    @patch("services.report_generator.determiner_utilisabilite")
    @patch("services.report_generator.calculer_couverture")
    @patch("services.report_generator.calculer_taux_succes")
    @patch("services.report_generator.get_aav")
    def test_format_csv_retourne_string(self, mock_aav, mock_taux, mock_couv, mock_util, mock_count, mock_learners):
        self._patch_metrics(mock_aav, mock_taux, mock_couv, mock_util, mock_count, mock_learners)

        from services.report_generator import collect_data_for_aav
        result = collect_data_for_aav(1, "csv")

        assert isinstance(result, str)
        assert "id_aav" in result
        assert "Types entiers" in result

    @patch("services.report_generator.count_distinct_learners")
    @patch("services.report_generator.count_attempts")
    @patch("services.report_generator.determiner_utilisabilite")
    @patch("services.report_generator.calculer_couverture")
    @patch("services.report_generator.calculer_taux_succes")
    @patch("services.report_generator.get_aav")
    def test_format_pdf_retourne_base64(self, mock_aav, mock_taux, mock_couv, mock_util, mock_count, mock_learners):
        self._patch_metrics(mock_aav, mock_taux, mock_couv, mock_util, mock_count, mock_learners)

        from services.report_generator import collect_data_for_aav
        result = collect_data_for_aav(1, "pdf")

        decoded = base64.b64decode(result)
        assert decoded[:4] == b"%PDF"

    @patch("services.report_generator.get_aav")
    def test_aav_inexistant_retourne_none(self, mock_aav):
        mock_aav.return_value = None

        from services.report_generator import collect_data_for_aav
        assert collect_data_for_aav(999, "json") is None

    @patch("services.report_generator.count_distinct_learners")
    @patch("services.report_generator.count_attempts")
    @patch("services.report_generator.determiner_utilisabilite")
    @patch("services.report_generator.calculer_couverture")
    @patch("services.report_generator.calculer_taux_succes")
    @patch("services.report_generator.get_aav")
    def test_format_inconnu_leve_value_error(self, mock_aav, *_):
        mock_aav.return_value = AAV_1

        from services.report_generator import collect_data_for_aav
        with pytest.raises(ValueError, match="Format de rapport inconnu"):
            collect_data_for_aav(1, "xml")


# ==============================================================
# TESTS — collect_data_for_student
# ==============================================================

class TestCollectDataForStudent:

    def _setup_student_mock(self, mock_get_student, mock_db):
        mock_get_student.return_value = STUDENT_BOB
        conn, cursor = make_conn_mock(fetchall=TENTATIVES_BOB)
        mock_db.return_value = conn

    @patch("services.report_generator.get_db_connection")
    @patch("services.report_generator.get_student")
    def test_format_json_retourne_dict_avec_tentatives(self, mock_get_student, mock_db):
        self._setup_student_mock(mock_get_student, mock_db)

        from services.report_generator import collect_data_for_student
        result = collect_data_for_student(2, "json")

        assert isinstance(result, dict)
        assert result["id_apprenant"] == 2
        assert result["nom"] == "bob_progressif"
        assert result["nb_tentatives"] == 3

    @patch("services.report_generator.get_db_connection")
    @patch("services.report_generator.get_student")
    def test_format_csv_retourne_string_avec_colonnes(self, mock_get_student, mock_db):
        self._setup_student_mock(mock_get_student, mock_db)

        from services.report_generator import collect_data_for_student
        result = collect_data_for_student(2, "csv")

        assert isinstance(result, str)
        assert "id_apprenant" in result
        assert "score_obtenu" in result

    @patch("services.report_generator.get_db_connection")
    @patch("services.report_generator.get_student")
    def test_format_pdf_retourne_base64(self, mock_get_student, mock_db):
        self._setup_student_mock(mock_get_student, mock_db)

        from services.report_generator import collect_data_for_student
        result = collect_data_for_student(2, "pdf")

        decoded = base64.b64decode(result)
        assert decoded[:4] == b"%PDF"

    @patch("services.report_generator.get_student")
    def test_apprenant_inexistant_retourne_none(self, mock_get_student):
        mock_get_student.return_value = None

        from services.report_generator import collect_data_for_student
        assert collect_data_for_student(999, "json") is None

    @patch("services.report_generator.get_db_connection")
    @patch("services.report_generator.get_student")
    def test_format_inconnu_leve_value_error(self, mock_get_student, mock_db):
        self._setup_student_mock(mock_get_student, mock_db)

        from services.report_generator import collect_data_for_student
        with pytest.raises(ValueError, match="Format de rapport inconnu"):
            collect_data_for_student(2, "html")


# ==============================================================
# TESTS — collect_data_for_discipline
# ==============================================================

class TestCollectDataForDiscipline:

    AAVS_PROGRAMMATION = [AAV_1, AAV_5]

    def _patch_all(self, mock_aavs, mock_taux, mock_couv, mock_util, mock_diff, mock_frag, mock_inut):
        mock_aavs.return_value = self.AAVS_PROGRAMMATION
        mock_taux.return_value = 0.70
        mock_couv.return_value = 0.85
        mock_util.return_value = True
        mock_diff.return_value = []
        mock_frag.return_value = []
        mock_inut.return_value = []

    @patch("services.report_generator.detecter_aavs_inutilises")
    @patch("services.report_generator.detecter_aavs_fragiles")
    @patch("services.report_generator.detecter_aavs_difficiles")
    @patch("services.report_generator.determiner_utilisabilite")
    @patch("services.report_generator.calculer_couverture")
    @patch("services.report_generator.calculer_taux_succes")
    @patch("services.report_generator.get_all_aavs")
    def test_format_json_retourne_dict_avec_aavs(
        self, mock_aavs, mock_taux, mock_couv, mock_util, mock_diff, mock_frag, mock_inut
    ):
        self._patch_all(mock_aavs, mock_taux, mock_couv, mock_util, mock_diff, mock_frag, mock_inut)

        from services.report_generator import collect_data_for_discipline
        result = collect_data_for_discipline("Programmation", "json")

        assert isinstance(result, dict)
        assert result["discipline"] == "Programmation"
        assert result["nb_aavs"] == 2
        assert len(result["aavs"]) == 2

    @patch("services.report_generator.detecter_aavs_inutilises")
    @patch("services.report_generator.detecter_aavs_fragiles")
    @patch("services.report_generator.detecter_aavs_difficiles")
    @patch("services.report_generator.determiner_utilisabilite")
    @patch("services.report_generator.calculer_couverture")
    @patch("services.report_generator.calculer_taux_succes")
    @patch("services.report_generator.get_all_aavs")
    def test_format_csv_contient_colonnes_alertes(
        self, mock_aavs, mock_taux, mock_couv, mock_util, mock_diff, mock_frag, mock_inut
    ):
        self._patch_all(mock_aavs, mock_taux, mock_couv, mock_util, mock_diff, mock_frag, mock_inut)

        from services.report_generator import collect_data_for_discipline
        result = collect_data_for_discipline("Programmation", "csv")

        assert isinstance(result, str)
        assert "alerte_difficile" in result
        assert "alerte_fragile" in result
        assert "alerte_inutilise" in result

    @patch("services.report_generator.detecter_aavs_inutilises")
    @patch("services.report_generator.detecter_aavs_fragiles")
    @patch("services.report_generator.detecter_aavs_difficiles")
    @patch("services.report_generator.determiner_utilisabilite")
    @patch("services.report_generator.calculer_couverture")
    @patch("services.report_generator.calculer_taux_succes")
    @patch("services.report_generator.get_all_aavs")
    def test_filtre_par_discipline(
        self, mock_aavs, mock_taux, mock_couv, mock_util, mock_diff, mock_frag, mock_inut
    ):
        """AAVs d'une autre discipline sont exclus du rapport."""
        aav_autre = {**AAV_1, "discipline": "Mathématiques"}
        mock_aavs.return_value = [AAV_1, AAV_5, aav_autre]
        mock_taux.return_value = 0.70
        mock_couv.return_value = 0.85
        mock_util.return_value = True
        mock_diff.return_value = []
        mock_frag.return_value = []
        mock_inut.return_value = []

        from services.report_generator import collect_data_for_discipline
        result = collect_data_for_discipline("Programmation", "json")

        assert result["nb_aavs"] == 2

    @patch("services.report_generator.detecter_aavs_inutilises")
    @patch("services.report_generator.detecter_aavs_fragiles")
    @patch("services.report_generator.detecter_aavs_difficiles")
    @patch("services.report_generator.determiner_utilisabilite")
    @patch("services.report_generator.calculer_couverture")
    @patch("services.report_generator.calculer_taux_succes")
    @patch("services.report_generator.get_all_aavs")
    def test_format_inconnu_leve_value_error(
        self, mock_aavs, mock_taux, mock_couv, mock_util, mock_diff, mock_frag, mock_inut
    ):
        self._patch_all(mock_aavs, mock_taux, mock_couv, mock_util, mock_diff, mock_frag, mock_inut)

        from services.report_generator import collect_data_for_discipline
        with pytest.raises(ValueError, match="Format de rapport inconnu"):
            collect_data_for_discipline("Programmation", "xlsx")


# ==============================================================
# TESTS — generer_rapport_personnalise
# ==============================================================

class TestGenererRapportPersonnalise:

    @patch("services.report_generator.RapportRepository")
    @patch("services.report_generator.to_json")
    @patch("services.report_generator.collect_data_for_aav")
    @patch("services.report_generator.get_aav")
    def test_type_aav_appelle_collect_data_for_aav(self, mock_get_aav, mock_collect, mock_json, mock_repo):
        mock_get_aav.return_value = AAV_1
        mock_collect.return_value = {"id_aav": 1, "nom": "Types entiers"}
        mock_json.return_value = "{}"
        fake_rapport = MagicMock()
        mock_repo.return_value.create.return_value = fake_rapport

        from services.report_generator import generer_rapport_personnalise
        result = generer_rapport_personnalise("aav", "1", datetime(2023, 1, 1), datetime(2023, 1, 31), "json")

        mock_collect.assert_called_once_with(1, "json")
        assert result == fake_rapport

    @patch("services.report_generator.RapportRepository")
    @patch("services.report_generator.to_json")
    @patch("services.report_generator.collect_data_for_student")
    @patch("services.report_generator.get_student")
    def test_type_student_appelle_collect_data_for_student(self, mock_get_student, mock_collect, mock_json, mock_repo):
        mock_get_student.return_value = STUDENT_BOB
        mock_collect.return_value = {"id_apprenant": 2, "nom": "bob_progressif"}
        mock_json.return_value = "{}"
        mock_repo.return_value.create.return_value = MagicMock()

        from services.report_generator import generer_rapport_personnalise
        generer_rapport_personnalise("student", "2", datetime(2023, 1, 1), datetime(2023, 1, 31), "json")

        mock_collect.assert_called_once_with(2, "json")

    @patch("services.report_generator.RapportRepository")
    @patch("services.report_generator.to_json")
    @patch("services.report_generator.collect_data_for_discipline")
    @patch("services.report_generator.get_all_aavs")
    def test_type_discipline_appelle_collect_data_for_discipline(self, mock_get_all_aavs, mock_collect, mock_json, mock_repo):
        mock_get_all_aavs.return_value = [{"id_aav": 1, "nom": "Test", "discipline": "Programmation"}]
        mock_collect.return_value = {"discipline": "Programmation"}
        mock_json.return_value = "{}"
        mock_repo.return_value.create.return_value = MagicMock()

        from services.report_generator import generer_rapport_personnalise
        generer_rapport_personnalise("discipline", "Programmation", datetime(2023, 1, 1), datetime(2023, 1, 31), "json")

        mock_collect.assert_called_once_with("Programmation", "json")

    @patch("services.report_generator.get_aav")
    @patch("services.report_generator.collect_data_for_aav")
    def test_data_none_retourne_none(self, mock_collect, mock_get_aav):
        mock_get_aav.return_value = None
        mock_collect.return_value = None

        from services.report_generator import generer_rapport_personnalise
        result = generer_rapport_personnalise("aav", "999", None, None, "json")

        assert result is None

    def test_type_inconnu_leve_value_error(self):
        from services.report_generator import generer_rapport_personnalise
        with pytest.raises(ValueError, match="Unknown report type"):
            generer_rapport_personnalise("inconnu", "1", None, None, "json")


# ==============================================================
# TESTS — generer_rapport_global
# ==============================================================

class TestGenererRapportGlobal:

    @patch("services.report_generator.detecter_aavs_inutilises")
    @patch("services.report_generator.detecter_aavs_fragiles")
    @patch("services.report_generator.detecter_aavs_difficiles")
    @patch("services.report_generator.count_attempts")
    @patch("services.report_generator.determiner_utilisabilite")
    @patch("services.report_generator.calculer_couverture")
    @patch("services.report_generator.calculer_taux_succes")
    @patch("services.report_generator.get_all_aavs")
    def test_retourne_rapport_global_response(
        self, mock_aavs, mock_taux, mock_couv, mock_util,
        mock_count, mock_diff, mock_frag, mock_inut
    ):
        mock_aavs.return_value = [AAV_1, AAV_5]
        mock_taux.return_value = 0.70
        mock_couv.return_value = 0.85
        mock_util.return_value = True
        mock_count.return_value = 5
        mock_diff.return_value = []
        mock_frag.return_value = []
        mock_inut.return_value = []

        from services.report_generator import generer_rapport_global
        result = generer_rapport_global()

        assert result.nb_aavs_total == 2
        assert result.nb_aavs_utilisables == 2
        assert len(result.aavs) == 2

    @patch("services.report_generator.detecter_aavs_inutilises")
    @patch("services.report_generator.detecter_aavs_fragiles")
    @patch("services.report_generator.detecter_aavs_difficiles")
    @patch("services.report_generator.count_attempts")
    @patch("services.report_generator.determiner_utilisabilite")
    @patch("services.report_generator.calculer_couverture")
    @patch("services.report_generator.calculer_taux_succes")
    @patch("services.report_generator.get_all_aavs")
    def test_compte_nb_alertes_correctement(
        self, mock_aavs, mock_taux, mock_couv, mock_util,
        mock_count, mock_diff, mock_frag, mock_inut
    ):
        mock_aavs.return_value = [AAV_1]
        mock_taux.return_value = 0.50
        mock_couv.return_value = 0.80
        mock_util.return_value = False
        mock_count.return_value = 3

        diff = MagicMock(); diff.model_dump.return_value = {}
        frag = MagicMock(); frag.model_dump.return_value = {}
        inut = MagicMock(); inut.model_dump.return_value = {}

        mock_diff.return_value = [diff]
        mock_frag.return_value = [frag, frag]
        mock_inut.return_value = [inut, inut, inut]

        from services.report_generator import generer_rapport_global
        result = generer_rapport_global()

        assert result.nb_alertes["difficiles"] == 1
        assert result.nb_alertes["fragiles"] == 2
        assert result.nb_alertes["inutilises"] == 3

    @patch("services.report_generator.detecter_aavs_inutilises")
    @patch("services.report_generator.detecter_aavs_fragiles")
    @patch("services.report_generator.detecter_aavs_difficiles")
    @patch("services.report_generator.count_attempts")
    @patch("services.report_generator.determiner_utilisabilite")
    @patch("services.report_generator.calculer_couverture")
    @patch("services.report_generator.calculer_taux_succes")
    @patch("services.report_generator.get_all_aavs")
    def test_nb_utilisables_correct(
        self, mock_aavs, mock_taux, mock_couv, mock_util,
        mock_count, mock_diff, mock_frag, mock_inut
    ):
        """2 AAVs dont 1 seul utilisable → nb_aavs_utilisables = 1."""
        mock_aavs.return_value = [AAV_1, AAV_5]
        mock_taux.return_value = 0.50
        mock_couv.return_value = 0.80
        mock_util.side_effect = [True, False]  # AAV1 utilisable, AAV5 non
        mock_count.return_value = 3
        mock_diff.return_value = []
        mock_frag.return_value = []
        mock_inut.return_value = []

        from services.report_generator import generer_rapport_global
        result = generer_rapport_global()

        assert result.nb_aavs_utilisables == 1

    @patch("services.report_generator.detecter_aavs_inutilises")
    @patch("services.report_generator.detecter_aavs_fragiles")
    @patch("services.report_generator.detecter_aavs_difficiles")
    @patch("services.report_generator.count_attempts")
    @patch("services.report_generator.determiner_utilisabilite")
    @patch("services.report_generator.calculer_couverture")
    @patch("services.report_generator.calculer_taux_succes")
    @patch("services.report_generator.get_all_aavs")
    def test_date_generation_presente(
        self, mock_aavs, mock_taux, mock_couv, mock_util,
        mock_count, mock_diff, mock_frag, mock_inut
    ):
        mock_aavs.return_value = []
        mock_diff.return_value = []
        mock_frag.return_value = []
        mock_inut.return_value = []

        from services.report_generator import generer_rapport_global
        result = generer_rapport_global()

        assert result.date_generation is not None
        assert isinstance(result.date_generation, str)