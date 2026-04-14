"""
Reports & Analytics page – style moderne.
Génère des rapports personnalisés et consulte le rapport global.
"""

import sys
from pathlib import Path
import flet as ft
import httpx, json

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

BASE_URL = "http://localhost:8000"


class ReportsPage:
    def __init__(self, content_area):
        self.content_area = content_area
        self._page = None
        self.affichage_resultat = None

    def _set_result(self, text: str, color: str = "#212121"):
        self.affichage_resultat.value = text
        self.affichage_resultat.color = color
        self._page.update()

    def get_rapport_global(self, e):
        self._set_result("Chargement du rapport global...")
        try:
            r = httpx.get(BASE_URL + "/reports/global", timeout=8)
            self._set_result(json.dumps(r.json(), indent=2, ensure_ascii=False))
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")

    def ouvrir_generation(self, e):
        champ_type = ft.TextField(label="Type rapport (aav / global)", value="aav", width=320)
        champ_id = ft.TextField(
            label="ID cible",
            width=180,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        champ_format = ft.TextField(label="Format (pdf / json)", value="pdf", width=180)

        def generer(ev):
            try:
                body = {
                    "type_rapport": champ_type.value or "aav",
                    "id_cible": int(champ_id.value) if champ_id.value else 1,
                    "format": champ_format.value or "pdf",
                }
                r = httpx.post(BASE_URL + "/reports/generate", json=body, timeout=10)
                self._set_result(json.dumps(r.json(), indent=2, ensure_ascii=False))
            except Exception as err:
                self._set_result(f"Erreur génération : {err}", "#F44336")
            finally:
                dialog.open = False
                self._page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Générer un rapport personnalisé"),
            content=ft.Column([champ_type, champ_id, champ_format], tight=True),
            actions=[
                ft.TextButton("Annuler", on_click=lambda _: setattr(dialog, "open", False) or self._page.update()),
                ft.ElevatedButton("Générer", on_click=generer, bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE),
            ],
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def build(self, page: ft.Page):
        self._page = page
        COLOR_PRIMARY = "#B71C1C"

        self.affichage_resultat = ft.Text("Résultat : aucun", size=14, color="#212121")

        boite_resultat = ft.Container(
            content=ft.Column([self.affichage_resultat], scroll=ft.ScrollMode.ALWAYS),
            width=600, height=380,
            bgcolor="#FFFFFF",
            border_radius=10,
            padding=16,
            border=ft.border.all(1, "#FFCDD2"),
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Rapports & Analytics", size=28, weight="bold", color=COLOR_PRIMARY),
                    ft.Divider(height=20, color="transparent"),
                    ft.Text("Générez des rapports personnalisés ou consultez les statistiques globales.", size=14, color="#616161"),
                    ft.Divider(height=15, color="transparent"),
                    ft.Row([
                        ft.ElevatedButton(
                            "Rapport Global",
                            icon=ft.Icons.PUBLIC,
                            on_click=self.get_rapport_global,
                            bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE,
                        ),
                        ft.ElevatedButton(
                            "Générer un Rapport",
                            icon=ft.Icons.PICTURE_AS_PDF,
                            on_click=self.ouvrir_generation,
                            bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE,
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
