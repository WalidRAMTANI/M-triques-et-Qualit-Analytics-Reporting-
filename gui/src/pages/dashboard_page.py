"""
Dashboard Enseignant page – style épuré.
Tableau de bord : stats enseignant, stats discipline, couverture ontologie.
Correspond exactement aux 3 endpoints du router dashboard.py.
"""

import sys
from pathlib import Path
import flet as ft

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.dashboard_data import get_teacher_stats, get_discipline_stats, get_ontology_cov


class DashboardPage:
    def __init__(self, content_area):
        self.content_area = content_area
        self._page = None
        self.affichage_resultat = None
        self.champ_enseignant = None
        self.champ_discipline = None
        self.champ_ontologie = None

    def _set_result(self, text: str, color: str = "#212121"):
        self.affichage_resultat.value = text
        self.affichage_resultat.color = color
        self._page.update()

    def _fmt(self, res) -> str:
        if isinstance(res, dict):
            return "\n".join(f"{k:35}: {v}" for k, v in res.items())
        # Pydantic model ou autre
        try:
            d = res.dict() if hasattr(res, "dict") else vars(res)
            return "\n".join(f"{k:35}: {v}" for k, v in d.items())
        except Exception:
            return str(res)

    # ── Endpoint 1 : GET /teachers/{id}/overview ─────────────────────────────

    def voir_stats_enseignant(self, e):
        if not self.champ_enseignant.value:
            self._set_result("⚠ Renseignez l'ID enseignant.", "#F44336")
            return
        try:
            res = get_teacher_stats(int(self.champ_enseignant.value))
            if res:
                self._set_result(
                    f"📋 TABLEAU DE BORD – Enseignant #{self.champ_enseignant.value}\n"
                    f"{'─' * 50}\n"
                    + self._fmt(res)
                )
            else:
                self._set_result(f"Aucune statistique trouvée pour l'enseignant #{self.champ_enseignant.value}", "#F44336")
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")

    # ── Endpoint 2 : GET /discipline/{discipline}/stats ───────────────────────

    def voir_stats_discipline(self, e):
        if not self.champ_discipline.value:
            self._set_result("⚠ Renseignez le nom de la discipline.", "#F44336")
            return
        try:
            res = get_discipline_stats(self.champ_discipline.value.strip())
            if res:
                self._set_result(
                    f"📊 STATISTIQUES – Discipline : {self.champ_discipline.value}\n"
                    f"{'─' * 50}\n"
                    + self._fmt(res)
                )
            else:
                self._set_result(f"Aucune statistique trouvée pour « {self.champ_discipline.value} »", "#F44336")
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")

    # ── Endpoint 3 : GET /ontology/{id}/coverage ─────────────────────────────

    def voir_couverture_ontologie(self, e):
        if not self.champ_ontologie.value:
            self._set_result("⚠ Renseignez l'ID ontologie.", "#F44336")
            return
        try:
            res = get_ontology_cov(int(self.champ_ontologie.value))
            if res:
                self._set_result(
                    f"🗺 COUVERTURE – Ontologie #{self.champ_ontologie.value}\n"
                    f"{'─' * 50}\n"
                    + self._fmt(res)
                )
            else:
                self._set_result(f"Couverture introuvable pour l'ontologie #{self.champ_ontologie.value}", "#F44336")
        except Exception as err:
            self._set_result(f"Erreur : {err}", "#F44336")

    # ── Build ─────────────────────────────────────────────────────────────────

    def build(self, page: ft.Page):
        self._page = page
        COLOR_PRIMARY = "#1565C0"
        COLOR_BG_INPUT = "#E3F2FD"
        COLOR_BORDER = "#2196F3"

        def field(label, icon=ft.Icons.PERSON, ktype=ft.KeyboardType.NUMBER, width=200):
            return ft.TextField(
                label=label, width=width,
                keyboard_type=ktype,
                border_radius=10,
                border_color=COLOR_BORDER,
                bgcolor=COLOR_BG_INPUT,
                prefix_icon=icon,
                cursor_color=COLOR_PRIMARY,
            )

        self.champ_enseignant = field("ID Enseignant", ft.Icons.PERSON, ft.KeyboardType.NUMBER)
        self.champ_discipline = field("Discipline (ex: Maths)", ft.Icons.BOOK, ft.KeyboardType.TEXT, 250)
        self.champ_ontologie = field("ID Ontologie", ft.Icons.ACCOUNT_TREE, ft.KeyboardType.NUMBER)
        self.affichage_resultat = ft.Text("Résultat : aucun", size=14, color="#212121")

        boite_resultat = ft.Container(
            content=ft.Column([self.affichage_resultat], scroll=ft.ScrollMode.ALWAYS),
            width=640, height=380,
            bgcolor="#FFFFFF",
            border_radius=10,
            padding=16,
            border=ft.border.all(1, "#BBDEFB"),
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Tableau de Bord", size=28, weight="bold", color=COLOR_PRIMARY),
                    ft.Divider(height=16, color="transparent"),

                    # Section Enseignant
                    ft.Text("👨‍🏫  Vue Enseignant", size=14, weight="bold", color="#424242"),
                    ft.Row([
                        self.champ_enseignant,
                        ft.ElevatedButton(
                            "Stats Enseignant",
                            icon=ft.Icons.PERSON,
                            on_click=self.voir_stats_enseignant,
                            bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE,
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER),

                    ft.Divider(height=8, color="transparent"),

                    # Section Discipline
                    ft.Text("📚  Vue Discipline", size=14, weight="bold", color="#424242"),
                    ft.Row([
                        self.champ_discipline,
                        ft.ElevatedButton(
                            "Stats Discipline",
                            icon=ft.Icons.BAR_CHART,
                            on_click=self.voir_stats_discipline,
                            bgcolor="#1976D2", color=ft.Colors.WHITE,
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER),

                    ft.Divider(height=8, color="transparent"),

                    # Section Ontologie
                    ft.Text("🗺  Couverture Ontologie", size=14, weight="bold", color="#424242"),
                    ft.Row([
                        self.champ_ontologie,
                        ft.ElevatedButton(
                            "Voir Couverture",
                            icon=ft.Icons.ACCOUNT_TREE,
                            on_click=self.voir_couverture_ontologie,
                            bgcolor="#0288D1", color=ft.Colors.WHITE,
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER),

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
