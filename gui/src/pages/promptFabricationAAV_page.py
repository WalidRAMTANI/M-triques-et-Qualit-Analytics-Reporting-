import sys
import flet as ft
import httpx
from pathlib import Path

# Configuration du chemin racine pour les imports internes
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Parametres de l'API
BASE_URL = "http://127.0.0.1:8000"

class PromptfabricationaavPage:
    """
    Page de gestion et de consultation des prompts de fabrication AAV.
    Assure l'interface entre le referentiel d'instructions et les mecanismes de generation.
    """

    def __init__(self, content_area):
        """Initialise la page avec les composants de recherche et le conteneur de resultats."""
        self.content_area = content_area
        self._page = None
        self.champ_id = ft.TextField(
            label="Identifiant du Prompt", width=200, border_color="#880E4F",
            keyboard_type=ft.KeyboardType.NUMBER
        )
        self.result_container = ft.Container(
            expand=True, padding=20, border_radius=12,
            border=ft.border.all(1, "#FCE4EC"), bgcolor="white"
        )

    def _set_result(self, control: ft.Control):
        """Met a jour la zone d'affichage avec un nouveau composant graphique."""
        self.result_container.content = control
        if self._page: self._page.update()

    def _show_msg(self, msg: str, is_error=False):
        """Affiche une notification coloree en cas de succes ou d'erreur."""
        cor, ico = ("#EF5350", ft.Icons.ERROR_OUTLINE) if is_error else ("#66BB6A", ft.Icons.CHECK_CIRCLE_OUTLINE)
        self._set_result(
            ft.Container(
                content=ft.Row([ft.Icon(ico, color="white"), ft.Text(msg, color="white", expand=True)]),
                bgcolor=cor, padding=12, border_radius=10
            )
        )

    def _display_data(self, data, title):
        """Genere dynamiquement la vue pour une liste ou un dictionnaire de prompts."""
        if isinstance(data, list):
            def select_item(id_val):
                self.champ_id.value = str(id_val)
                self.search(None)

            items = [
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.TEXT_SNIPPET, color="#880E4F"),
                    title=ft.Text(f"Instruction #{d.get('id_prompt', '?')}", weight="bold"),
                    subtitle=ft.Text(f"{str(d.get('prompt_texte', ''))[:80]}...", max_lines=1),
                    on_click=lambda e, idx=d.get('id_prompt'): select_item(idx),
                    hover_color="#FCE4EC"
                )
                for d in data
            ]
            return ft.Column([
                ft.Row([ft.Icon(ft.Icons.LIST_ALT, color="#880E4F"), ft.Text(title, weight="bold", size=20)]),
                ft.Divider(color="#FCE4EC"),
                ft.ListView(items, expand=True)
            ], expand=True)
        
        # Affichage detaille pour un dictionnaire unique
        rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(k).replace("_", " ").title(), weight="bold", width=150)),
                ft.DataCell(ft.Text(str(v)))
            ])
            for k, v in data.items()
        ]
        return ft.Column([
            ft.Row([ft.Icon(ft.Icons.DESCRIPTION, color="#880E4F"), ft.Text(title, weight="bold", size=20, color="#880E4F")]),
            ft.Divider(color="#FCE4EC"),
            ft.DataTable(columns=[ft.DataColumn(ft.Text("Parametre/Champ")), ft.DataColumn(ft.Text("Contenu"))], rows=rows)
        ], scroll=ft.ScrollMode.AUTO)

    def search(self, e):
        """Effectue une recherche ciblee via l'identifiant numerique du prompt."""
        if not self.champ_id.value:
            self._show_msg("Veuillez saisir un identifiant valide.", True); return
        self._set_result(ft.ProgressRing(color="#880E4F"))
        try:
            r = httpx.get(f"{BASE_URL}/promptFabricationAAV/{self.champ_id.value}", timeout=10)
            if r.status_code == 200:
                self._set_result(self._display_data(r.json(), f"Details du Referentiel #{self.champ_id.value}"))
            else:
                self._show_msg(f"L'instruction #{self.champ_id.value} est introuvable.", True)
        except Exception as err:
            self._show_msg(f"Erreur reseau : {err}", True)

    def list_all(self, e):
        """Recupere et affiche l'integralite de la bibliotheque des prompts."""
        self._set_result(ft.ProgressRing(color="#880E4F"))
        try:
            r = httpx.get(f"{BASE_URL}/promptFabricationAAV/", timeout=10)
            if r.status_code == 200:
                self._set_result(self._display_data(r.json(), "Bibliotheque des Instructions"))
            else:
                self._show_msg("La recuperation bibliographique a echoue.", True)
        except:
            self._show_msg("Serveur de donnees inaccessible.", True)

    def build(self, page: ft.Page):
        """Assemble l'interface graphique de gestion des prompts."""
        self._page = page
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(content=ft.Icon(ft.Icons.SETTINGS_SUGGEST, color="white", size=30), bgcolor="#880E4F", padding=10, border_radius=10),
                    ft.Text("Referentiel des Prompts AAV", size=28, weight="bold", color="#880E4F"),
                ]),
                ft.Text("Supervision et edition des instructions generatrices d'exercices academiques.", size=14, color="grey"),
                ft.Row([
                    self.champ_id,
                    ft.ElevatedButton("Rechercher", icon=ft.Icons.SEARCH, on_click=self.search, bgcolor="#880E4F", color="white", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))),
                    ft.ElevatedButton("Parcourir Bibliotheque", icon=ft.Icons.LIBRARY_BOOKS, on_click=self.list_all, bgcolor="#AD1457", color="white", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))),
                ], spacing=15),
                self.result_container
            ], spacing=20),
            padding=30, expand=True
        )
