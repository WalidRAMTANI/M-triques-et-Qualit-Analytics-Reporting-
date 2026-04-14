"""
Types & Dictionnaires page – style moderne.
Consulte les types d'activités, niveaux de maîtrise et disciplines.
"""

import sys
from pathlib import Path
import flet as ft
import httpx, json

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

BASE_URL = "http://localhost:8000"


class TypesPage:
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

    def get_activity_types(self, e):
        self._set_result("Chargement...")
        self._set_result(self._get("/types/activity-types"))

    def get_mastery_levels(self, e):
        self._set_result("Chargement...")
        self._set_result(self._get("/types/mastery-levels"))

    def get_disciplines(self, e):
        self._set_result("Chargement...")
        self._set_result(self._get("/types/disciplines"))

    def build(self, page: ft.Page):
        self._page = page
        COLOR_PRIMARY = "#00695C"
        COLOR_BG_INPUT = "#E0F2F1"
        COLOR_BORDER = "#009688"

        self.affichage_resultat = ft.Text("Résultat : aucun", size=14, color="#212121")

        boite_resultat = ft.Container(
            content=ft.Column([self.affichage_resultat], scroll=ft.ScrollMode.ALWAYS),
            width=600, height=380,
            bgcolor="#FFFFFF",
            border_radius=10,
            padding=16,
            border=ft.border.all(1, "#B2DFDB"),
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Types & Dictionnaires", size=28, weight="bold", color=COLOR_PRIMARY),
                    ft.Divider(height=20, color="transparent"),
                    ft.Text(
                        "Consultez les référentiels : types d'activités, niveaux de maîtrise, disciplines.",
                        size=14, color="#616161",
                    ),
                    ft.Divider(height=15, color="transparent"),
                    ft.Row([
                        ft.ElevatedButton(
                            "Types d'Activités",
                            icon=ft.Icons.CATEGORY,
                            on_click=self.get_activity_types,
                            bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE,
                        ),
                        ft.ElevatedButton(
                            "Niveaux de Maîtrise",
                            icon=ft.Icons.STAR,
                            on_click=self.get_mastery_levels,
                            bgcolor="#00897B", color=ft.Colors.WHITE,
                        ),
                        ft.ElevatedButton(
                            "Disciplines",
                            icon=ft.Icons.BOOK,
                            on_click=self.get_disciplines,
                            bgcolor=ft.Colors.TEAL_700, color=ft.Colors.WHITE,
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
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
