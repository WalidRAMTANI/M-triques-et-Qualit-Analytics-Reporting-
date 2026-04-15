import sys
import json
import httpx
import flet as ft
from pathlib import Path

# Configuration du chemin racine pour les imports internes
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Parametres de l'API
BASE_URL = "http://127.0.0.1:8000"

class RemediationPage:
    """
    Page destinee au diagnostic pedagogique et a la remediation.
    Analyse les causes racines des echecs et propose des plans d'action personnalises.
    """

    def __init__(self, content_area):
        """Initialise la page avec les champs de saisie pour l'apprenant et l'AAV cible."""
        self.content_area = content_area
        self._page = None
        self.champ_apprenant = ft.TextField(
            label="ID Apprenant", value="1", width=180, 
            border_color="#BF360C", keyboard_type=ft.KeyboardType.NUMBER
        )
        self.champ_aav = ft.TextField(
            label="ID AAV", width=180, border_color="#BF360C", 
            keyboard_type=ft.KeyboardType.NUMBER
        )
        self.result_container = ft.Container(
            expand=True, padding=15, border_radius=10, 
            border=ft.border.all(1, "#FFCCBC"), bgcolor="#FAFAFA"
        )

    def _set_result(self, control: ft.Control):
        """Met a jour la zone de resultats avec le nouveau composant Flet."""
        self.result_container.content = control
        if self._page:
            self._page.update()

    def _show_msg(self, msg: str, is_error=False, is_info=False):
        """Affiche un message d'information ou d'erreur structure."""
        color = "#EF5350" if is_error else "#2196F3" if is_info else "#66BB6A"
        icon = ft.Icons.ERROR_OUTLINE if is_error else ft.Icons.INFO_OUTLINE if is_info else ft.Icons.CHECK_CIRCLE_OUTLINE
        self._set_result(
            ft.Container(
                content=ft.Row([ft.Icon(icon, color="white"), ft.Text(msg, color="white", weight="500")]), 
                bgcolor=color, padding=15, border_radius=10
            )
        )

    def _create_diagnostic_card(self, d):
        """Genere une carte visuelle detaillant un diagnostic specifique."""
        date = str(d.get('date_diagnostic', 'Inconnu'))[:16].replace('T', ' ')
        aav_source = d.get('id_aav_source', '?')
        score = d.get('score_obtenu', 0)
        
        racines = d.get('aav_racines_defaillants', [])
        if isinstance(racines, str): 
            try: racines = json.loads(racines)
            except: racines = []
        
        recos = d.get('recommandations', [])
        if isinstance(recos, str):
            try: recos = json.loads(recos)
            except: recos = []

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.ANALYTICS, color="#D84315"),
                        title=ft.Text(f"Echec sur AAV #{aav_source}", weight="bold"),
                        subtitle=ft.Text(f"Diagnostic du {date}"),
                        trailing=ft.Text(f"{score*100:.0f}%", size=20, weight="bold", color="#B71C1C")
                    ),
                    ft.Container(
                        padding=ft.padding.only(left=20, right=20, bottom=10), 
                        content=ft.Column([
                            ft.Text("Causes racines detectees :", weight="bold", size=14),
                            ft.Row([ft.Chip(label=ft.Text(f"AAV #{r}"), bgcolor="#FFEBEE") for r in (racines if racines else [])], wrap=True),
                            ft.Divider(height=20, color="#FFCCBC"),
                            ft.Text("Recommandations :", weight="bold", size=14),
                            ft.Column([ft.Row([ft.Icon(ft.Icons.CHECK, color="green", size=16), ft.Text(str(re), size=13)]) for re in (recos if recos else [])])
                        ])
                    ),
                ]),
                padding=10
            ),
            elevation=2
        )

    def _format_data(self, data, mode="list"):
        """Formate les donnees brutes de l'API selon le mode d'affichage selectionne."""
        if not data: 
            return ft.Text("Aucune donnee disponible.", italic=True, color="grey")
        
        if mode == "diagnostics":
            if isinstance(data, list):
                if not data: return ft.Text("Historique vide.")
                cards = [self._create_diagnostic_card(d) for d in data]
                return ft.ListView(cards, expand=True, spacing=10)
            return self._create_diagnostic_card(data)

        if mode == "weaknesses":
            items = [ft.ListTile(
                leading=ft.Icon(ft.Icons.REPORT_PROBLEM, color="#C62828"),
                title=ft.Text(f"AAV #{w.get('id_aav', '?')}", weight="bold"),
                subtitle=ft.Text(f"Maitrise : {w.get('maitrise', 0)*100:.0f}%"),
            ) for w in data]
            return ft.ListView(items, expand=True) if items else ft.Text("Aucun point faible critique.")

        if mode == "map":
            heatmap = data.get("heatmap", data.get("progression_map", []))
            items = [ft.ListTile(
                leading=ft.Icon(ft.Icons.CIRCLE, color="red" if h.get('couleur_recommandee') == 'rouge' else "orange" if h.get('couleur_recommandee') == 'jaune' else "green"),
                title=ft.Text(f"AAV #{h.get('id_aav')}"),
                subtitle=ft.Text(f"Maitrise: {h.get('niveau_maitrise', 0)*100:.1f}%")
            ) for h in heatmap]
            return ft.ListView(items, expand=True) if items else ft.Text("Carte non generee.")

        return ft.Text(str(data))

    def run_action(self, path, title, mode):
        """Execute une requete vers l'API de remediation et met a jour l'UI."""
        if not self.champ_apprenant.value:
            self._show_msg("ID apprenant requis.", True); return
        self._set_result(ft.ProgressRing(color="#BF360C"))
        try:
            url_target = path.format(id=self.champ_apprenant.value, aav=self.champ_aav.value)
            r = httpx.get(f"{BASE_URL}/remediation{url_target}", timeout=10)
            if r.status_code == 200:
                self._set_result(ft.Column([
                    ft.Text(title, weight="bold", size=20, color="#BF360C"),
                    ft.Divider(color="#FFCCBC"),
                    self._format_data(r.json(), mode)
                ], expand=True))
            elif r.status_code == 404:
                self._show_msg("Donnees introuvables.", False, True)
            else:
                self._show_msg(f"Erreur Serveur ({r.status_code})", True)
        except Exception as e:
            self._show_msg(f"Erreur technique : {e}", True)

    def build(self, page: ft.Page):
        """Construit le layout de la page de remediation."""
        self._page = page
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(content=ft.Icon(ft.Icons.HEALING, color="white", size=30), bgcolor="#BF360C", padding=10, border_radius=12),
                    ft.Text("Remediation et Diagnostics", size=28, weight="bold", color="#BF360C"),
                ]),
                ft.Row([
                    self.champ_apprenant, 
                    self.champ_aav,
                    ft.ElevatedButton("Diagnostics", icon=ft.Icons.HISTORY, on_click=lambda _: self.run_action("/learners/{id}/diagnostics", "Historique", "diagnostics"), bgcolor="#BF360C", color="white"),
                    ft.ElevatedButton("Faiblesses", icon=ft.Icons.BUG_REPORT, on_click=lambda _: self.run_action("/learners/{id}/weaknesses", "Points Faibles", "weaknesses"), bgcolor="#D84315", color="white"),
                    ft.ElevatedButton("Carte", icon=ft.Icons.MAP, on_click=lambda _: self.run_action("/learners/{id}/progression-map", "Maitrise Map", "map"), bgcolor="#E64A19", color="white"),
                ], wrap=True),
                self.result_container
            ], spacing=20),
            padding=30, expand=True
        )
