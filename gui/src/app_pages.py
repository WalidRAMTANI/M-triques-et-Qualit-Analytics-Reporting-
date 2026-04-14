"""
Pages module for AAV Dashboard GUI.

Contains page definitions:
- Sidebar: Navigation sidebar with buttons for all pages
- AlertsPage: Dashboard showing alerts and students at risk
- DetailsPage: Detailed view of a single AAV
- AboutPage: About/project information page
"""

import flet as ft
from utils import fetch, row, section, ALERTS_API, AAVS_API


# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────

class Sidebar:
    """Left navigation sidebar with buttons linking to every page."""

    def __init__(self, show_alerts_cb, show_about_cb,
                 show_aav_detail_cb=None, show_dashboard_cb=None,
                 show_metrics_cb=None, show_sessions_cb=None):
        self.show_alerts    = show_alerts_cb
        self.show_about     = show_about_cb
        self.show_aav_detail = show_aav_detail_cb
        self.show_dashboard  = show_dashboard_cb
        self.show_metrics    = show_metrics_cb
        self.show_sessions   = show_sessions_cb

    # ── helpers ───────────────────────────────────────────────────────────────

    def _nav_btn(self, icon, label, on_click, color="#9C27B0"):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=color, size=20),
                ft.Text(label, color=ft.Colors.WHITE, size=14),
            ], spacing=12),
            on_click=on_click,
            ink=True,
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            bgcolor=ft.Colors.WHITE10,
            margin=ft.margin.only(bottom=6),
        )

    def _section_label(self, text):
        return ft.Container(
            content=ft.Text(text.upper(), size=10, color=ft.Colors.WHITE38,
                            weight=ft.FontWeight.W_600),
            padding=ft.padding.only(left=12, top=16, bottom=4),
        )

    # ── build ─────────────────────────────────────────────────────────────────

    def build(self):
        logo = ft.Column([
            ft.Icon(ft.Icons.SCHOOL, color="#9C27B0", size=36),
            ft.Text("AAV Dashboard", size=16, weight=ft.FontWeight.W_600,
                    color=ft.Colors.WHITE),
            ft.Text("Monitoring Platform", size=11, color=ft.Colors.WHITE38),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2)

        nav_items = [
            self._section_label("Monitoring"),
            self._nav_btn(ft.Icons.NOTIFICATIONS_ACTIVE, "Alertes",
                          self.show_alerts, "#E57373"),
        ]

        # Optional pages (only shown when callback is provided)
        if self.show_aav_detail:
            nav_items.append(
                self._nav_btn(ft.Icons.AUTO_STORIES, "Détail AAV",
                              self.show_aav_detail, "#64B5F6")
            )

        if self.show_dashboard:
            nav_items += [
                self._section_label("Pédagogie"),
                self._nav_btn(ft.Icons.DASHBOARD, "Tableau de Bord",
                              self.show_dashboard, "#81C784"),
            ]

        if self.show_metrics:
            nav_items.append(
                self._nav_btn(ft.Icons.ANALYTICS, "Métriques & Qualité",
                              self.show_metrics, "#FFB74D")
            )

        if self.show_sessions:
            nav_items.append(
                self._nav_btn(ft.Icons.PLAY_CIRCLE_FILL, "Sessions",
                              self.show_sessions, "#CE93D8")
            )

        nav_items += [
            self._section_label("Application"),
            self._nav_btn(ft.Icons.INFO_OUTLINE, "À propos",
                          self.show_about, "#90A4AE"),
        ]

        return ft.Column(
            [
                ft.Container(content=logo, padding=ft.padding.symmetric(vertical=24)),
                ft.Divider(color=ft.Colors.WHITE12, height=1),
                ft.Container(
                    content=ft.Column(nav_items, spacing=0),
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                ),
            ],
            spacing=0,
        )


# ──────────────────────────────────────────────────────────────────────────────
# ALERTS PAGE
# ──────────────────────────────────────────────────────────────────────────────

class AlertsPage:
    """Alert Dashboard page showing difficult, unused, and fragile AAVs."""

    def __init__(self, content_area, show_details_callback, show_about_callback=None):
        self.content_area = content_area
        self.show_details = show_details_callback
        self.show_about   = show_about_callback
        self.onto_field   = ft.TextField(label="Ontologie ID", width=200, dense=True)
        self.risk_col     = ft.Column()
        self.page_content = None
        self._page        = None

    def load_risk(self, e=None):
        """Load students at risk for given ontology ID."""
        self.risk_col.controls.clear()
        data = fetch(f"/students-at-risk/{self.onto_field.value}", ALERTS_API)

        if not data:
            self.risk_col.controls.append(
                ft.Text("Aucun résultat.", color=ft.Colors.WHITE38))
        else:
            for d in data:
                progression = d.get('progression', 0)
                color_progression = (
                    ft.Colors.GREEN_300  if progression > 0.7 else
                    ft.Colors.ORANGE_300 if progression > 0.4 else
                    ft.Colors.RED_300
                )
                learner_info = ft.Column([
                    ft.Row([
                        ft.Text(f"Apprenant #{d['id_apprenant']}", size=14,
                                weight=ft.FontWeight.W_500, expand=True),
                        ft.Text(f"⚠️ {d.get('aavs_bloques', 0)} bloqué(s)",
                                color=ft.Colors.RED_300, weight=ft.FontWeight.W_500),
                    ]),
                    ft.Divider(height=1),
                    row("Nom", d.get('nom', 'N/A')),
                    row("Progression globale",
                        f"{round(progression * 100, 1)}%", color_progression),
                    row("AAVs bloqués", str(d.get('aavs_bloques', 0)),
                        ft.Colors.RED_300 if d.get('aavs_bloques', 0) > 0
                        else ft.Colors.WHITE),
                ], spacing=4)

                self.risk_col.controls.append(ft.Container(
                    content=learner_info,
                    bgcolor=ft.Colors.WHITE10,
                    border_radius=10,
                    padding=12,
                    margin=ft.margin.only(bottom=8),
                ))

        if self._page:
            self._page.update()

    def make_clickable_aav_row(self, aav_data, color):
        """Create a clickable row for an AAV."""
        def on_click(e):
            self.show_details(aav_data['id_aav'])

        return ft.Container(
            content=ft.Row([
                ft.Text(aav_data["nom"], expand=True, color=ft.Colors.WHITE70),
                ft.Text(f"{int(aav_data.get('taux_succes', 0)*100)}%",
                        color=color, weight=ft.FontWeight.W_500),
            ]),
            on_click=on_click,
            ink=True,
        )

    def build(self, page):
        """Build the alerts page."""
        self._page = page

        difficult = fetch("/difficult-aavs", ALERTS_API)
        unused    = fetch("/unused-aavs",    ALERTS_API)
        fragile   = fetch("/fragile-aavs",   ALERTS_API)

        self.page_content = ft.Column([
            ft.Text("Alert Dashboard", size=24, weight=ft.FontWeight.W_500),
            ft.Text("AAV monitoring", color=ft.Colors.WHITE38, size=13),
            ft.Row([
                ft.Container(
                    ft.Column([
                        ft.Text(str(len(difficult)), size=28, weight=ft.FontWeight.W_500),
                        ft.Text("Difficult", color=ft.Colors.WHITE38, size=12),
                    ]),
                    bgcolor=ft.Colors.RED_900, border_radius=8, padding=16, expand=True,
                ),
                ft.Container(
                    ft.Column([
                        ft.Text(str(len(unused)), size=28, weight=ft.FontWeight.W_500),
                        ft.Text("Unused", color=ft.Colors.WHITE38, size=12),
                    ]),
                    bgcolor=ft.Colors.ORANGE_900, border_radius=8, padding=16, expand=True,
                ),
                ft.Container(
                    ft.Column([
                        ft.Text(str(len(fragile)), size=28, weight=ft.FontWeight.W_500),
                        ft.Text("Fragile", color=ft.Colors.WHITE38, size=12),
                    ]),
                    bgcolor=ft.Colors.BLUE_900, border_radius=8, padding=16, expand=True,
                ),
            ], spacing=10),
            section("Difficult AAVs (cliquer pour voir les détails)", [
                self.make_clickable_aav_row(d, ft.Colors.RED_300) for d in difficult
            ]),
            section("Unused AAVs", [
                row(d["nom"], f"{d.get('nombre_utilisations', 0)} uses",
                    ft.Colors.ORANGE_300) for d in unused
            ]),
            section("Fragile AAVs", [
                row(d["nom"], f"σ={round(d.get('variance', 0), 1)}",
                    ft.Colors.BLUE_300) for d in fragile
            ]),
            ft.Row(
                [self.onto_field,
                 ft.ElevatedButton("Rechercher", on_click=self.load_risk)],
                vertical_alignment=ft.CrossAxisAlignment.END,
            ),
            self.risk_col,
        ], scroll=ft.ScrollMode.AUTO)

        return self.page_content


# ──────────────────────────────────────────────────────────────────────────────
# DETAILS PAGE  (single AAV via REST)
# ──────────────────────────────────────────────────────────────────────────────

class DetailsPage:
    """Detailed view of a single AAV (fetched from REST API)."""

    def __init__(self, content_area, show_alerts_callback):
        self.content_area = content_area
        self.show_alerts  = show_alerts_callback
        self.page_content = None

    def build(self, aav_id, page):
        """Build the details page for a given AAV ID."""
        self.page_content = ft.Column(scroll=ft.ScrollMode.AUTO)
        aav_data = fetch(f"/{aav_id}", AAVS_API)

        if not aav_data or isinstance(aav_data, list):
            self.page_content.controls.append(
                ft.Text("AAV introuvable", color=ft.Colors.RED_300))
        else:
            prerequis_ids = aav_data.get('prerequis_ids', [])
            prerequis_ids_str = (", ".join(map(str, prerequis_ids))
                                 if prerequis_ids else "Aucun")

            prerequis_externes = aav_data.get('prerequis_externes_codes', [])
            prerequis_externes_str = (", ".join(prerequis_externes)
                                      if prerequis_externes else "Aucun")

            is_active    = aav_data.get('is_active', True)
            status_color = ft.Colors.GREEN_300 if is_active else ft.Colors.RED_300
            status_text  = "Active" if is_active else "Inactive"

            self.page_content.controls.append(ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text(aav_data.get('nom', 'N/A'), size=24,
                                weight=ft.FontWeight.W_500),
                        ft.Text(f"ID: {aav_data.get('id_aav', 'N/A')}",
                                color=ft.Colors.WHITE38, size=12),
                    ], expand=True),
                    ft.Column([
                        ft.ElevatedButton("← Retour Alertes",
                                          on_click=self.show_alerts),
                        ft.Container(
                            content=ft.Text(status_text, size=12,
                                            weight=ft.FontWeight.W_500),
                            bgcolor=status_color,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            border_radius=4,
                        ),
                    ]),
                ], expand=True),
                ft.Divider(),

                ft.Text("Informations de base", size=14, weight=ft.FontWeight.W_500),
                row("Libellé d'intégration",
                    aav_data.get('libelle_integration', 'N/A')),
                row("Discipline",   aav_data.get('discipline',   'N/A')),
                row("Enseignement", aav_data.get('enseignement', 'N/A')),
                row("Type AAV",     aav_data.get('type_aav',     'N/A')),
                row("Type Évaluation",
                    aav_data.get('type_evaluation', 'N/A')),

                ft.Divider(),
                ft.Text("Prérequis", size=14, weight=ft.FontWeight.W_500),
                row("IDs Prérequis", prerequis_ids_str),
                row("Codes Externes", prerequis_externes_str),
                row("Code Prérequis Interdisciplinaire",
                    aav_data.get('code_prerequis_interdisciplinaire', 'N/A')),

                ft.Divider(),
                ft.Text("Métadonnées", size=14, weight=ft.FontWeight.W_500),
                row("Version", str(aav_data.get('version', 'N/A'))),
                row("Créé le",
                    str(aav_data.get('created_at', 'N/A'))[:10]
                    if aav_data.get('created_at') else 'N/A'),
                row("Modifié le",
                    str(aav_data.get('updated_at', 'N/A'))[:10]
                    if aav_data.get('updated_at') else 'N/A'),

                ft.Divider(),
                ft.Text("Description", size=14, weight=ft.FontWeight.W_500),
                ft.Container(
                    content=ft.Text(
                        aav_data.get('description_markdown', 'N/A'),
                        size=12, color=ft.Colors.WHITE70),
                    bgcolor=ft.Colors.WHITE10,
                    border_radius=10,
                    padding=12,
                ),
            ], spacing=8))

        return self.page_content


# ──────────────────────────────────────────────────────────────────────────────
# ABOUT PAGE
# ──────────────────────────────────────────────────────────────────────────────

class AboutPage:
    """About / project information page."""

    def __init__(self, content_area, show_alerts_callback):
        self.content_area = content_area
        self.show_alerts  = show_alerts_callback

    def build(self, page):
        """Build the about page."""

        def _info_card(icon, title, body, color="#9C27B0"):
            return ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(icon, color=color, size=28),
                        ft.Text(title, size=16, weight=ft.FontWeight.W_600,
                                color=ft.Colors.WHITE),
                    ], spacing=10),
                    ft.Divider(height=1, color=ft.Colors.WHITE12),
                    ft.Text(body, size=13, color=ft.Colors.WHITE70),
                ], spacing=8),
                bgcolor=ft.Colors.WHITE10,
                border_radius=10,
                padding=20,
                expand=True,
            )

        features = [
            (ft.Icons.NOTIFICATIONS_ACTIVE, "Alertes AAV",
             "Visualisez en temps réel les AAVs difficiles, inutilisés ou fragiles "
             "et identifiez les apprenants en difficulté par ontologie.",
             "#EF9A9A"),
            (ft.Icons.AUTO_STORIES, "Détail AAV",
             "Consultez, modifiez et supprimez n'importe quel AAV directement "
             "depuis l'interface grâce aux appels REST.",
             "#90CAF9"),
            (ft.Icons.DASHBOARD, "Tableau de Bord",
             "Suivez les statistiques pédagogiques par enseignant : AAVs gérés, "
             "apprenants, taux de succès et alertes actives.",
             "#A5D6A7"),
            (ft.Icons.ANALYTICS, "Métriques & Qualité",
             "Calculez et historisez les métriques qualité de chaque AAV, "
             "et exportez des rapports PDF personnalisés.",
             "#FFCC80"),
            (ft.Icons.PLAY_CIRCLE_FILL, "Sessions",
             "Gérez le cycle de vie des sessions d'apprentissage : création, "
             "démarrage, clôture et suppression.",
             "#CE93D8"),
        ]

        cards_row1 = ft.Row(
            [_info_card(icon, title, body, color)
             for icon, title, body, color in features[:3]],
            spacing=14,
        )
        cards_row2 = ft.Row(
            [_info_card(icon, title, body, color)
             for icon, title, body, color in features[3:]],
            spacing=14,
        )

        return ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.SCHOOL, color="#9C27B0", size=48),
                        ft.Column([
                            ft.Text("AAV Dashboard", size=32,
                                    weight=ft.FontWeight.W_700,
                                    color=ft.Colors.WHITE),
                            ft.Text("Plateforme de monitoring pédagogique",
                                    size=15, color=ft.Colors.WHITE54),
                        ], spacing=2),
                    ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Container(height=8),
                    ft.Text(
                        "Cette application centralise la gestion et le suivi des "
                        "Activités d'Apprentissage Virtuelles (AAV). "
                        "Naviguez entre les différentes sections via la barre latérale.",
                        size=14, color=ft.Colors.WHITE70,
                    ),
                ], spacing=8),
                bgcolor=ft.Colors.WHITE10,
                border_radius=12,
                padding=28,
            ),

            ft.Container(height=6),
            ft.Text("Fonctionnalités", size=18, weight=ft.FontWeight.W_600,
                    color=ft.Colors.WHITE70),
            cards_row1,
            cards_row2,

            ft.Container(height=10),
            ft.Row([
                ft.ElevatedButton(
                    "Aller aux Alertes →",
                    icon=ft.Icons.NOTIFICATIONS_ACTIVE,
                    on_click=self.show_alerts,
                    bgcolor="#9C27B0",
                    color=ft.Colors.WHITE,
                ),
            ]),
        ], scroll=ft.ScrollMode.AUTO, spacing=12)