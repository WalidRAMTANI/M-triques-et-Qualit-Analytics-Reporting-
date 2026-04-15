import sys
import requests
import flet as ft
from pathlib import Path

# Configuration du chemin racine pour les imports internes
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

class DashboardPage:
    """
    Page de tableau de bord permettant aux enseignants de consulter les statistiques globales.
    Supporte l'affichage des syntheses par enseignant, par discipline et la couverture d'ontologie.
    """

    def __init__(self, content_area):
        """Initialise la classe avec les references d'affichage et les etats UI."""
        self.content_area = content_area
        self._page = None
        self.affichage_resultat = None
        self.champ_enseignant = None
        self.champ_discipline = None
        self.champ_ontologie = None

    def _set_result(self, text: str, color: str = "#212121"):
        """Met a jour la zone de texte affichant les resultats de l'analyse."""
        self.affichage_resultat.value = text
        self.affichage_resultat.color = color
        self._page.update()

    def _fmt(self, res) -> str:
        """Formate les donnees JSON pour un rendu texte structure et lisible."""
        if isinstance(res, dict):
            return "\n".join(f"{k:35}: {v}" for k, v in res.items())
        try:
            d = res.dict() if hasattr(res, "dict") else vars(res)
            return "\n".join(f"{k:35}: {v}" for k, v in d.items())
        except Exception:
            return str(res)

    def voir_stats_enseignant(self, e):
        """Recupere les statistiques generales associees a un identifiant enseignant."""
        if not self.champ_enseignant.value:
            self._set_result("ID enseignant requis.", "#F44336")
            return
        try:
            url = f"http://127.0.0.1:8000/dashboard/teachers/{int(self.champ_enseignant.value)}/overview"
            response = requests.get(url)
            if response.status_code == 200:
                self._set_result(
                    f"TABLEAU DE BORD - Enseignant #{self.champ_enseignant.value}\n"
                    f"{'---' * 15}\n"
                    + self._fmt(response.json())
                )
            elif response.status_code == 404:
                self._set_result("Enseignant introuvable.", "#F44336")
            else:
                self._set_result(f"Erreur de chargement ({response.status_code})", "#F44336")
        except Exception as err:
            self._set_result(f"Erreur technique : {err}", "#F44336")

    def voir_stats_discipline(self, e):
        """Affiche les metriques de performance globales pour une discipline specifique."""
        if not self.champ_discipline.value:
            self._set_result("Nom de la discipline requis.", "#F44336")
            return
        try:
            disc = self.champ_discipline.value.strip()
            url = f"http://127.0.0.1:8000/dashboard/discipline/{disc}/stats"
            response = requests.get(url)
            if response.status_code == 200:
                self._set_result(
                    f"STATISTIQUES - Discipline : {disc}\n"
                    f"{'---' * 15}\n"
                    + self._fmt(response.json())
                )
            elif response.status_code == 404:
                self._set_result(f"Aucune statistique pour {disc}.", "#F44336")
            else:
                self._set_result(f"Erreur ({response.status_code})", "#F44336")
        except Exception as err:
            self._set_result(f"Erreur technique : {err}", "#F44336")

    def voir_couverture_ontologie(self, e):
        """Analyse le taux de couverture des AAV pour une ontologie donnee."""
        if not self.champ_ontologie.value:
            self._set_result("ID ontologie requis.", "#F44336")
            return
        try:
            id_onto = int(self.champ_ontologie.value)
            url = f"http://127.0.0.1:8000/dashboard/ontology/{id_onto}/coverage"
            response = requests.get(url)
            if response.status_code == 200:
                self._set_result(
                    f"COUVERTURE - Ontologie #{id_onto}\n"
                    f"{'---' * 15}\n"
                    + self._fmt(response.json())
                )
            elif response.status_code == 404:
                self._set_result(f"Ontologie #{id_onto} introuvable.", "#F44336")
            else:
                self._set_result(f"Erreur de chargement.", "#F44336")
        except Exception as err:
            self._set_result(f"Erreur technique : {err}", "#F44336")

    def build(self, page: ft.Page):
        """Genere l'interface utilisateur du tableau de bord."""
        self._page = page
        COLOR_PRIMARY = "#1565C0"

        def input_field(label, icon, ktype=ft.KeyboardType.NUMBER, width=200):
            return ft.TextField(
                label=label, width=width, keyboard_type=ktype,
                border_radius=10, border_color="#2196F3", bgcolor="#E3F2FD",
                prefix_icon=icon
            )

        self.champ_enseignant = input_field("ID Enseignant", ft.Icons.PERSON)
        self.champ_discipline = input_field("Discipline", ft.Icons.BOOK, ft.KeyboardType.TEXT, 250)
        self.champ_ontologie = input_field("ID Ontologie", ft.Icons.ACCOUNT_TREE)
        self.affichage_resultat = ft.Text("Resultat de l'analyse.", size=14)

        boite_resultat = ft.Container(
            content=ft.Column([self.affichage_resultat], scroll=ft.ScrollMode.ALWAYS),
            width=640, height=380, bgcolor="#FFFFFF", border_radius=10, padding=16,
            border=ft.border.all(1, "#BBDEFB")
        )

        return ft.Container(
            content=ft.Column([
                ft.Text("Tableau de Bord Analytique", size=28, weight="bold", color=COLOR_PRIMARY),
                ft.Text("Vue Enseignant", size=14, weight="bold"),
                ft.Row([self.champ_enseignant, ft.ElevatedButton("Analyse", on_click=self.voir_stats_enseignant, bgcolor=COLOR_PRIMARY, color="white")]),
                ft.Text("Vue Discipline", size=14, weight="bold"),
                ft.Row([self.champ_discipline, ft.ElevatedButton("Stats", on_click=self.voir_stats_discipline, bgcolor="#1976D2", color="white")]),
                ft.Text("Couverture Ontologique", size=14, weight="bold"),
                ft.Row([self.champ_ontologie, ft.ElevatedButton("Verifier", on_click=self.voir_couverture_ontologie, bgcolor="#0288D1", color="white")]),
                boite_resultat,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
            padding=20, expand=True
        )
