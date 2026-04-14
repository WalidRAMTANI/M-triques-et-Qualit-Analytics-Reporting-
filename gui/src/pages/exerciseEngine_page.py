"""
Moteur d'Exercices page – style moderne.
Règles de progression, séquences, évaluation des exercices.
"""

import sys
from pathlib import Path
import flet as ft
import httpx, json

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

BASE_URL = "http://localhost:8000"


class ExerciseenginePage:
    def __init__(self, content_area):
        self.content_area = content_area
        self._page = None
        self.affichage_resultat = None
        self.champ_aav = None
        self.champ_apprenant = None
        self.champ_prompt = None

    def _set_result(self, text: str, color: str = "#212121"):
        self.affichage_resultat.value = text
        self.affichage_resultat.color = color
        self._page.update()

    def _get(self, path):
        r = httpx.get(BASE_URL + path, timeout=5)
        return json.dumps(r.json(), indent=2, ensure_ascii=False)

    def _post(self, path, body=None):
        r = httpx.post(BASE_URL + path, json=body or {}, timeout=5)
        return json.dumps(r.json(), indent=2, ensure_ascii=False)

    def voir_prompts_aav(self, e):
        if not self.champ_aav.value:
            self._set_result("⚠ Renseignez l'ID AAV.", "#F44336"); return
        try:
            self._set_result(self._get(f"/aavs/{self.champ_aav.value}/prompts"))
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")

    def voir_regles(self, e):
        try:
            self._set_result(self._get("/progression-rules"))
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")

    def voir_regles_aav(self, e):
        if not self.champ_aav.value:
            self._set_result("⚠ Renseignez l'ID AAV.", "#F44336"); return
        try:
            self._set_result(self._get(f"/progression-rules/{self.champ_aav.value}"))
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")

    def prochain_exercice(self, e):
        if not self.champ_aav.value:
            self._set_result("⚠ Renseignez l'ID AAV.", "#F44336"); return
        try:
            self._set_result(self._get(f"/next-exercise/{self.champ_aav.value}"))
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")

    def voir_sequence(self, e):
        if not self.champ_apprenant.value or not self.champ_aav.value:
            self._set_result("⚠ Renseignez l'ID apprenant ET l'ID AAV.", "#F44336"); return
        try:
            self._set_result(self._get(f"/sequence/{self.champ_apprenant.value}/{self.champ_aav.value}"))
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")

    def preview_prompt(self, e):
        if not self.champ_prompt.value:
            self._set_result("⚠ Renseignez l'ID prompt.", "#F44336"); return
        try:
            self._set_result(self._post(f"/prompts/{self.champ_prompt.value}/preview"))
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")

    def taux_succes_prompt(self, e):
        if not self.champ_prompt.value:
            self._set_result("⚠ Renseignez l'ID prompt.", "#F44336"); return
        try:
            self._set_result(self._get(f"/prompts/{self.champ_prompt.value}/success-rate"))
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")

    def selectionner_exercices(self, e):
        try:
            self._set_result(self._post("/exercises/select"))
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")

    def build(self, page: ft.Page):
        self._page = page
        COLOR_PRIMARY = "#004D40"
        COLOR_BG_INPUT = "#E0F2F1"
        COLOR_BORDER = "#009688"

        def field(label, icon=ft.Icons.SEARCH):
            return ft.TextField(
                label=label, width=170,
                keyboard_type=ft.KeyboardType.NUMBER,
                border_radius=10, border_color=COLOR_BORDER,
                bgcolor=COLOR_BG_INPUT, prefix_icon=icon,
                cursor_color=COLOR_PRIMARY,
            )

        self.champ_aav = field("ID AAV", ft.Icons.SCHOOL)
        self.champ_apprenant = field("ID Apprenant", ft.Icons.PERSON)
        self.champ_prompt = field("ID Prompt", ft.Icons.TEXT_SNIPPET)
        self.affichage_resultat = ft.Text("Résultat : aucun", size=14, color="#212121")

        boite_resultat = ft.Container(
            content=ft.Column([self.affichage_resultat], scroll=ft.ScrollMode.ALWAYS),
            width=620, height=380,
            bgcolor="#FFFFFF", border_radius=10, padding=16,
            border=ft.border.all(1, "#B2DFDB"),
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Moteur d'Exercices", size=28, weight="bold", color=COLOR_PRIMARY),
                    ft.Divider(height=16, color="transparent"),
                    ft.Row([self.champ_aav, self.champ_apprenant, self.champ_prompt], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
                    ft.Divider(height=10, color="transparent"),
                    ft.Text("Règles & Séquences :", size=13, weight="bold", color="#616161"),
                    ft.Row([
                        ft.ElevatedButton("Toutes les règles", icon=ft.Icons.RULE, on_click=self.voir_regles, bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE),
                        ft.ElevatedButton("Règles de l'AAV", icon=ft.Icons.RULE_FOLDER, on_click=self.voir_regles_aav, bgcolor="#00695C", color=ft.Colors.WHITE),
                        ft.ElevatedButton("Prochain exercice", icon=ft.Icons.ARROW_FORWARD, on_click=self.prochain_exercice, bgcolor="#00796B", color=ft.Colors.WHITE),
                        ft.ElevatedButton("Séquence Apprenant/AAV", icon=ft.Icons.PLAYLIST_PLAY, on_click=self.voir_sequence, bgcolor="#00897B", color=ft.Colors.WHITE),
                    ], alignment=ft.MainAxisAlignment.CENTER, wrap=True),
                    ft.Divider(height=6, color="transparent"),
                    ft.Text("Prompts & Évaluation :", size=13, weight="bold", color="#616161"),
                    ft.Row([
                        ft.ElevatedButton("Prompts de l'AAV", icon=ft.Icons.TEXT_SNIPPET, on_click=self.voir_prompts_aav, bgcolor="#26A69A", color=ft.Colors.WHITE),
                        ft.ElevatedButton("Aperçu Prompt", icon=ft.Icons.PREVIEW, on_click=self.preview_prompt, bgcolor="#4DB6AC", color=ft.Colors.WHITE),
                        ft.ElevatedButton("Taux de Succès", icon=ft.Icons.ANALYTICS, on_click=self.taux_succes_prompt, bgcolor=ft.Colors.AMBER_700, color=ft.Colors.WHITE),
                        ft.ElevatedButton("Sélectionner Exercices", icon=ft.Icons.CHECKLIST, on_click=self.selectionner_exercices, bgcolor="#0288D1", color=ft.Colors.WHITE),
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
