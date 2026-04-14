"""
Navigation Apprenants page – style moderne.
Accès aux AAVs accessibles, en cours, bloquées, révisables et dashboard.
"""

import sys
from pathlib import Path
import flet as ft
import httpx, json

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

BASE_URL = "http://localhost:8000"


class NavigationPage:
    def __init__(self, content_area):
        self.content_area = content_area
        self._page = None
        self.affichage_resultat = None
        self.champ_id = None

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

    def _require_id(self) -> str | None:
        if not self.champ_id.value:
            self._set_result("⚠ Veuillez renseigner l'ID apprenant.", "#F44336")
            return None
        return self.champ_id.value

    def voir_accessibles(self, e):
        if id_v := self._require_id():
            self._set_result(self._get(f"/navigation/{id_v}/accessible"))

    def voir_en_cours(self, e):
        if id_v := self._require_id():
            self._set_result(self._get(f"/navigation/{id_v}/in-progress"))

    def voir_bloquees(self, e):
        if id_v := self._require_id():
            self._set_result(self._get(f"/navigation/{id_v}/blocked"))

    def voir_revisables(self, e):
        if id_v := self._require_id():
            self._set_result(self._get(f"/navigation/{id_v}/reviewable"))

    def voir_dashboard(self, e):
        if id_v := self._require_id():
            self._set_result(self._get(f"/navigation/{id_v}/dashboard"))

    def voir_tout(self, e):
        if id_v := self._require_id():
            self._set_result(self._get(f"/navigation/{id_v}"))

    def build(self, page: ft.Page):
        self._page = page
        COLOR_PRIMARY = "#1B5E20"
        COLOR_BG_INPUT = "#E8F5E9"
        COLOR_BORDER = "#4CAF50"

        self.champ_id = ft.TextField(
            label="ID Apprenant",
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=10,
            border_color=COLOR_BORDER,
            bgcolor=COLOR_BG_INPUT,
            prefix_icon=ft.Icons.PERSON,
            cursor_color=COLOR_PRIMARY,
        )
        self.affichage_resultat = ft.Text("Résultat : aucun", size=14, color="#212121")

        boite_resultat = ft.Container(
            content=ft.Column([self.affichage_resultat], scroll=ft.ScrollMode.ALWAYS),
            width=600, height=380,
            bgcolor="#FFFFFF",
            border_radius=10,
            padding=16,
            border=ft.border.all(1, "#C8E6C9"),
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Navigation Apprenants", size=28, weight="bold", color=COLOR_PRIMARY),
                    ft.Divider(height=20, color="transparent"),
                    self.champ_id,
                    ft.Divider(height=10, color="transparent"),
                    ft.Row([
                        ft.ElevatedButton("Accessibles", icon=ft.Icons.LOCK_OPEN, on_click=self.voir_accessibles, bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE),
                        ft.ElevatedButton("En cours", icon=ft.Icons.PLAY_ARROW, on_click=self.voir_en_cours, bgcolor="#2E7D32", color=ft.Colors.WHITE),
                        ft.ElevatedButton("Bloquées", icon=ft.Icons.LOCK, on_click=self.voir_bloquees, bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE),
                    ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
                    ft.Row([
                        ft.ElevatedButton("À réviser", icon=ft.Icons.REFRESH, on_click=self.voir_revisables, bgcolor=ft.Colors.AMBER_700, color=ft.Colors.WHITE),
                        ft.ElevatedButton("Dashboard", icon=ft.Icons.DASHBOARD, on_click=self.voir_dashboard, bgcolor="#0288D1", color=ft.Colors.WHITE),
                        ft.ElevatedButton("Vue complète", icon=ft.Icons.LIST, on_click=self.voir_tout, bgcolor="#546E7A", color=ft.Colors.WHITE),
                    ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
                    ft.Divider(height=15, color="transparent"),
                    boite_resultat,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
                scroll=ft.ScrollMode.AUTO,
            ),
            bgcolor="#FFFFFF",
            expand=True,
            padding=20,
        )
