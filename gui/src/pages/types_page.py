import sys
import httpx
import flet as ft
from pathlib import Path

# Configuration du chemin racine pour les imports internes
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Parametres de l'API
BASE_URL = "http://127.0.0.1:8000"

class TypesPage:
    """
    Page de consultation des referentiels et dictionnaires metier.
    Permet de lister les types d'activites, les niveaux de maitrise et les disciplines enregistrees.
    """

    def __init__(self, content_area):
        """Initialise la page avec un conteneur de resultats vide."""
        self.content_area = content_area
        self._page = None
        self.result_container = ft.Container(
            expand=True, padding=20, border_radius=12, 
            border=ft.border.all(1, "#B2DFDB"), bgcolor="white"
        )

    def _set_result(self, control: ft.Control):
        """Met a jour la zone d'affichage avec le composant specifie."""
        self.result_container.content = control
        if self._page:
            self._page.update()

    def load_types(self, path, title, icon):
        """Charge dynamiquement les donnees d'un referentiel via l'API."""
        self._set_result(ft.ProgressRing(color="#00695C"))
        try:
            r = httpx.get(f"{BASE_URL}{path}", timeout=10)
            if r.status_code == 200:
                data = r.json()
                raw_list = []
                
                # Extraction selon la structure de reponse de l'API
                if "types" in data: 
                    raw_list = data["types"]
                elif "disciplines" in data: 
                    raw_list = data["disciplines"]
                elif "levels" in data:
                    levels_dict = data["levels"]
                    raw_list = [f"{k.title()}: {v}" for k, v in levels_dict.items()]
                else:
                    raw_list = data if isinstance(data, list) else [str(data)]

                items = [
                    ft.ListTile(
                        leading=ft.Icon(icon, color="#00695C"), 
                        title=ft.Text(str(item).replace("_", " ").title())
                    ) for item in raw_list
                ]
                
                self._set_result(ft.Column([
                    ft.Text(title, size=20, weight="bold", color="#00695C"),
                    ft.Divider(color="#E0F2F1"),
                    ft.ListView(items, expand=True)
                ], expand=True))
            else:
                self._set_result(ft.Text(f"Erreur API ({r.status_code})"))
        except Exception as e:
            self._set_result(ft.Text(f"Erreur technique : {e}"))

    def build(self, page: ft.Page):
        """Genere l'interface utilisateur de la page de referentiels."""
        self._page = page
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(content=ft.Icon(ft.Icons.BOOKMARK_ADDED, color="white", size=30), bgcolor="#00695C", padding=10, border_radius=10),
                    ft.Text("Referentiels et Dictionnaires", size=26, weight="bold", color="#00695C"),
                ]),
                ft.Row([
                    ft.ElevatedButton("Types d'Activites", icon=ft.Icons.CATEGORY, on_click=lambda _: self.load_types("/types/activity-types", "Dictionnaire des Activites", ft.Icons.CATEGORY), bgcolor="#00695C", color="white"),
                    ft.ElevatedButton("Maitrise", icon=ft.Icons.STAR, on_click=lambda _: self.load_types("/types/mastery-levels", "Niveaux de Maitrise", ft.Icons.STAR), bgcolor="#00796B", color="white"),
                    ft.ElevatedButton("Disciplines", icon=ft.Icons.LANGUAGE, on_click=lambda _: self.load_types("/types/disciplines", "Liste des Disciplines", ft.Icons.LANGUAGE), bgcolor="#00897B", color="white"),
                ], wrap=True),
                self.result_container
            ], spacing=20),
            padding=30, expand=True
        )
