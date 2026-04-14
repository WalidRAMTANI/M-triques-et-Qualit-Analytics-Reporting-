"""
Comparaison page – style épuré (fond blanc, champs de recherche, boîte résultat).
Compare les métriques entre AAVs et entre apprenants via /metrics/compare/*.
"""

import sys
from pathlib import Path
import flet as ft
import httpx, json

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


BASE_URL = "http://localhost:8000"


class ComparaisonPage:
    def __init__(self, content_area):
        self.content_area = content_area
        self._page = None
        self.affichage_resultat = None

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

    def comparer_aavs(self, e):
        self._set_result("Chargement...")
        self._set_result(self._get("/metrics/compare/aavs"))

    def comparer_learners(self, e):
        self._set_result("Chargement...")
        self._set_result(self._get("/metrics/compare/learners"))

    def build(self, page: ft.Page):
        self._page = page
        COLOR_PRIMARY = "#6A1B9A"
        COLOR_BG_INPUT = "#F3E5F5"
        COLOR_BORDER = "#9C27B0"

        self.affichage_resultat = ft.Text("Résultat : aucun", size=14, color="#212121")

        boite_resultat = ft.Container(
            content=ft.Column([self.affichage_resultat], scroll=ft.ScrollMode.ALWAYS),
            width=600, height=380,
            bgcolor="#FFFFFF",
            border_radius=10,
            padding=16,
            border=ft.border.all(1, "#E1BEE7"),
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Comparaison des Métriques", size=28, weight="bold", color=COLOR_PRIMARY),
                    ft.Divider(height=20, color="transparent"),
                    ft.Text(
                        "Comparez les performances des AAVs ou des apprenants.",
                        size=14, color="#616161",
                    ),
                    ft.Divider(height=15, color="transparent"),
                    ft.Row([
                        ft.ElevatedButton(
                            "Comparer les AAVs",
                            icon=ft.Icons.COMPARE_ARROWS,
                            on_click=self.comparer_aavs,
                            bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE,
                        ),
                        ft.ElevatedButton(
                            "Comparer les Apprenants",
                            icon=ft.Icons.PEOPLE,
                            on_click=self.comparer_learners,
                            bgcolor="#8E24AA", color=ft.Colors.WHITE,
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(height=15, color="transparent"),
                    boite_resultat,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
            ),
            bgcolor="#FFFFFF",
            expand=True,
            padding=20,
        )
