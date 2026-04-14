"""
Remédiation & Diagnostics page – style moderne.
Déclenche des remédations, consulte diagnostics et parcours de progression.
"""

import sys
from pathlib import Path
import flet as ft
import httpx, json

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

BASE_URL = "http://localhost:8000"


class RemediationPage:
    def __init__(self, content_area):
        self.content_area = content_area
        self._page = None
        self.affichage_resultat = None
        self.champ_apprenant = None
        self.champ_aav = None
        self.champ_diagnostic = None

    def _set_result(self, text: str, color: str = "#212121"):
        self.affichage_resultat.value = text
        self.affichage_resultat.color = color
        self._page.update()

    def _get(self, path: str) -> str:
        try:
            r = httpx.get(BASE_URL + path, timeout=5)
            return json.dumps(r.json(), indent=2, ensure_ascii=False)
        except Exception as err:
            return f"Erreur : {err}"

    def _post(self, path: str, body: dict = None) -> str:
        try:
            r = httpx.post(BASE_URL + path, json=body or {}, timeout=5)
            return json.dumps(r.json(), indent=2, ensure_ascii=False)
        except Exception as err:
            return f"Erreur : {err}"

    def voir_diagnostics(self, e):
        if not self.champ_apprenant.value:
            self._set_result("⚠ Renseignez l'ID apprenant.", "#F44336"); return
        self._set_result(self._get(f"/learners/{self.champ_apprenant.value}/diagnostics"))

    def voir_faiblesses(self, e):
        if not self.champ_apprenant.value:
            self._set_result("⚠ Renseignez l'ID apprenant.", "#F44336"); return
        self._set_result(self._get(f"/learners/{self.champ_apprenant.value}/weaknesses"))

    def voir_carte_progression(self, e):
        if not self.champ_apprenant.value:
            self._set_result("⚠ Renseignez l'ID apprenant.", "#F44336"); return
        self._set_result(self._get(f"/learners/{self.champ_apprenant.value}/progression-map"))

    def voir_root_causes(self, e):
        if not self.champ_apprenant.value or not self.champ_aav.value:
            self._set_result("⚠ Renseignez l'ID apprenant ET l'ID AAV.", "#F44336"); return
        self._set_result(self._get(f"/learners/{self.champ_apprenant.value}/aavs/{self.champ_aav.value}/root-causes"))

    def voir_activites_remediation(self, e):
        if not self.champ_diagnostic.value:
            self._set_result("⚠ Renseignez l'ID diagnostic.", "#F44336"); return
        self._set_result(self._get(f"/remediation/activities/{self.champ_diagnostic.value}"))

    def voir_arbre_diagnostic(self, e):
        if not self.champ_diagnostic.value:
            self._set_result("⚠ Renseignez l'ID diagnostic.", "#F44336"); return
        self._set_result(self._get(f"/diagnostics/{self.champ_diagnostic.value}/tree"))

    def declencher_remediation(self, e):
        self._set_result(self._post("/diagnostics/remediation"))

    def generer_parcours(self, e):
        self._set_result(self._post("/remediation/generate-path"))

    def analyser_parcours(self, e):
        self._set_result(self._post("/diagnostics/analyze-path"))

    def build(self, page: ft.Page):
        self._page = page
        COLOR_PRIMARY = "#BF360C"
        COLOR_BG_INPUT = "#FBE9E7"
        COLOR_BORDER = "#E64A19"

        def field(label, icon=ft.Icons.SEARCH):
            return ft.TextField(
                label=label, width=180,
                keyboard_type=ft.KeyboardType.NUMBER,
                border_radius=10, border_color=COLOR_BORDER,
                bgcolor=COLOR_BG_INPUT, prefix_icon=icon,
                cursor_color=COLOR_PRIMARY,
            )

        self.champ_apprenant = field("ID Apprenant", ft.Icons.PERSON)
        self.champ_aav = field("ID AAV", ft.Icons.SCHOOL)
        self.champ_diagnostic = field("ID Diagnostic", ft.Icons.MEDICAL_SERVICES)
        self.affichage_resultat = ft.Text("Résultat : aucun", size=14, color="#212121")

        boite_resultat = ft.Container(
            content=ft.Column([self.affichage_resultat], scroll=ft.ScrollMode.ALWAYS),
            width=620, height=380,
            bgcolor="#FFFFFF", border_radius=10, padding=16,
            border=ft.border.all(1, "#FFCCBC"),
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Remédiation & Diagnostics", size=28, weight="bold", color=COLOR_PRIMARY),
                    ft.Divider(height=16, color="transparent"),
                    ft.Row([self.champ_apprenant, self.champ_aav, self.champ_diagnostic], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
                    ft.Divider(height=10, color="transparent"),
                    ft.Text("Par apprenant :", size=13, weight="bold", color="#616161"),
                    ft.Row([
                        ft.ElevatedButton("Diagnostics", icon=ft.Icons.ANALYTICS, on_click=self.voir_diagnostics, bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE),
                        ft.ElevatedButton("Faiblesses", icon=ft.Icons.WARNING, on_click=self.voir_faiblesses, bgcolor="#D84315", color=ft.Colors.WHITE),
                        ft.ElevatedButton("Carte Progression", icon=ft.Icons.MAP, on_click=self.voir_carte_progression, bgcolor="#E64A19", color=ft.Colors.WHITE),
                        ft.ElevatedButton("Causes Racines", icon=ft.Icons.ACCOUNT_TREE, on_click=self.voir_root_causes, bgcolor="#BF360C", color=ft.Colors.WHITE),
                    ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
                    ft.Divider(height=6, color="transparent"),
                    ft.Text("Par diagnostic :", size=13, weight="bold", color="#616161"),
                    ft.Row([
                        ft.ElevatedButton("Activités Remédiation", icon=ft.Icons.FITNESS_CENTER, on_click=self.voir_activites_remediation, bgcolor="#6D4C41", color=ft.Colors.WHITE),
                        ft.ElevatedButton("Arbre Diagnostic", icon=ft.Icons.ACCOUNT_TREE, on_click=self.voir_arbre_diagnostic, bgcolor="#5D4037", color=ft.Colors.WHITE),
                    ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
                    ft.Divider(height=6, color="transparent"),
                    ft.Text("Actions globales :", size=13, weight="bold", color="#616161"),
                    ft.Row([
                        ft.ElevatedButton("Déclencher Remédiation", icon=ft.Icons.PLAY_CIRCLE, on_click=self.declencher_remediation, bgcolor=ft.Colors.AMBER_700, color=ft.Colors.WHITE),
                        ft.ElevatedButton("Générer Parcours", icon=ft.Icons.ROUTE, on_click=self.generer_parcours, bgcolor=ft.Colors.AMBER_800, color=ft.Colors.WHITE),
                        ft.ElevatedButton("Analyser Parcours", icon=ft.Icons.SEARCH, on_click=self.analyser_parcours, bgcolor="#795548", color=ft.Colors.WHITE),
                    ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
                    ft.Divider(height=15, color="transparent"),
                    boite_resultat,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
                scroll=ft.ScrollMode.AUTO,
            ),
            bgcolor="#FFFFFF",
            expand=True,
            padding=20,
        )
