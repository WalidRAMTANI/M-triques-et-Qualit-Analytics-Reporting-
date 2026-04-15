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

class StatutsPage:
    """
    Page de suivi des statuts d'apprentissage individuels.
    Permet de consulter le niveau de maitrise des AAV par apprenant.
    """

    def __init__(self, content_area):
        """Initialise la page avec les composants de recherche et la zone de resultats."""
        self.content_area = content_area
        self._page = None
        self.champ_id = ft.TextField(
            label="ID Statut ou Apprenant", width=220, 
            border_color="#1565C0", keyboard_type=ft.KeyboardType.NUMBER
        )
        self.result_container = ft.Container(
            expand=True, padding=20, border_radius=12, 
            border=ft.border.all(1, "#E3F2FD"), bgcolor="white"
        )

    def _set_result(self, control: ft.Control):
        """Met a jour la zone d'affichage avec les nouvelles donnees chargees."""
        self.result_container.content = control
        if self._page:
            self._page.update()

    def _format_data(self, data, title):
        """Formate dynamiquement les donnees API (liste ou dictionnaire) pour l'affichage."""
        if isinstance(data, list):
            items = []
            for d in data:
                id_s = d.get('id', '???')
                items.append(ft.ListTile(
                    leading=ft.Icon(ft.Icons.PERSON_SEARCH, color="#1565C0"),
                    title=ft.Text(f"Statut #{id_s} (Apprenant #{d.get('id_apprenant', '?')})"),
                    subtitle=ft.Text(f"AAV #{d.get('id_aav_cible', '?')} - Maitrise: {d.get('niveau_maitrise', 0)*100}%"),
                    on_click=lambda e, idx=id_s: self.search_by_id(idx)
                ))
            return ft.Column([ft.Text(title, weight="bold", size=18), ft.ListView(items, expand=True)], expand=True)
        
        rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(k.replace("_", " ").title(), weight="bold")), ft.DataCell(ft.Text(str(v)))]) for k, v in data.items()]
        return ft.Column([
            ft.Text(title, weight="bold", size=18, color="#1565C0"),
            ft.Divider(color="#E3F2FD"),
            ft.DataTable(columns=[ft.DataColumn(ft.Text("Critere")), ft.DataColumn(ft.Text("Detail"))], rows=rows)
        ], scroll=ft.ScrollMode.AUTO)

    def search_by_id(self, sid):
        """Lance une recherche automatique pour un identifiant de statut donne."""
        self.champ_id.value = str(sid)
        self.search(None)

    def search(self, e):
        """Recherche les statuts de maniere intelligente (par ID de statut ou par ID apprenant)."""
        if not self.champ_id.value:
            self._set_result(ft.Text("Identifiant requis.")); return
        self._set_result(ft.ProgressRing(color="#1565C0"))
        try:
            r = httpx.get(f"{BASE_URL}/learning-status/{self.champ_id.value}", timeout=10)
            if r.status_code == 200:
                self._set_result(self._format_data(r.json(), f"Fiche Statut #{self.champ_id.value}"))
            else:
                r2 = httpx.get(f"{BASE_URL}/learning-status", params={"id_apprenant": self.champ_id.value}, timeout=10)
                if r2.status_code == 200 and r2.json():
                    self._set_result(self._format_data(r2.json(), f"Statuts - Apprenant #{self.champ_id.value}"))
                else:
                    self._set_result(ft.Text("Aucun resultat pour cet ID."))
        except Exception as err:
            self._set_result(ft.Text(f"Erreur technique : {err}"))

    def load_list(self, e):
        """Charge l'integralite de la liste des statuts d'apprentissage."""
        self._set_result(ft.ProgressRing(color="#1565C0"))
        try:
            r = httpx.get(f"{BASE_URL}/learning-status", timeout=10)
            if r.status_code == 200:
                self._set_result(self._format_data(r.json(), "Referentiel des Statuts"))
            else:
                self._set_result(ft.Text("Erreur lors du chargement."))
        except:
            self._set_result(ft.Text("Serveur inaccessible."))

    def build(self, page: ft.Page):
        """Gere la construction visuelle de la page."""
        self._page = page
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(content=ft.Icon(ft.Icons.SCHOOL, color="white", size=30), bgcolor="#1565C0", padding=10, border_radius=10),
                    ft.Text("Statuts d'Apprentissage", size=26, weight="bold", color="#1565C0"),
                ]),
                ft.Row([
                    self.champ_id,
                    ft.ElevatedButton("Rechercher", icon=ft.Icons.SEARCH, on_click=self.search, bgcolor="#1565C0", color="white"),
                    ft.ElevatedButton("Voir Tout", icon=ft.Icons.LIST, on_click=self.load_list, bgcolor="#1E88E5", color="white"),
                ]),
                self.result_container
            ], spacing=20),
            padding=30, expand=True
        )
