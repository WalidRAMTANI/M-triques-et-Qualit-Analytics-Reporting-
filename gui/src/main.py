import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import flet as ft
from pages import AlertsPage, DetailsPage, Sidebar, AboutPage
from pages.aavs_page import AavsPage
from pages.activitePedagogique_page import ActivitepedagogiquePage
from pages.attempts_page import AttemptsPage
from pages.comparaison_page import ComparaisonPage
from pages.exerciseEngine_page import ExerciseenginePage
from pages.learners_page import LearnersPage
from pages.navigation_page import NavigationPage
from pages.ontologies_page import OntologiesPage
from pages.promptFabricationAAV_page import PromptfabricationaavPage
from pages.remediation_page import RemediationPage
from pages.reports_page import ReportsPage
from pages.statuts_page import StatutsPage
from pages.types_page import TypesPage
from pages.dashboard_page import DashboardPage
from pages.sessions_page import SessionsPage

# ── Import optional standalone view builders (Graph Views) ────────────────────
try:
    from dashboard_view import create_dashboard_view
    _HAS_DASHBOARD_GRAPH = True
except Exception:
    _HAS_DASHBOARD_GRAPH = False

try:
    from metrics_view import create_metrics_view
    _HAS_METRICS_GRAPH = True
except Exception:
    _HAS_METRICS_GRAPH = False

try:
    from aav_graph_view import build_aav_graph_view
    _HAS_AAV_GRAPH = True
except Exception as e:
    print(f"DEBUG: AAV Graph view error: {e}")
    _HAS_AAV_GRAPH = False

try:
    from session import build_session_view
    _HAS_SESSIONS_GRAPH = True
except Exception:
    _HAS_SESSIONS_GRAPH = False


def main(page: ft.Page):
    page.title   = "AAV Dashboard"
    page.bgcolor = "#1a1a2e"
    page.theme   = ft.Theme(color_scheme_seed="#9C27B0")
    page.window.width  = 1200
    page.window.height = 800
    page.padding = 0

    # ── Content area ─────────────────────────────────────────────────────────
    content_area = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

    def _set(view_control):
        content_area.controls.clear()
        content_area.controls.append(view_control)
        page.update()

    # ── Page callbacks ────────────────────────────────────────────────────────

    def show_aavs(e=None):
        page_inst = AavsPage(content_area)
        _set(page_inst.build(page))

    def show_dashboard_page(e=None):
        page_inst = DashboardPage(content_area)
        _set(page_inst.build(page))

    def show_sessions_page(e=None):
        page_inst = SessionsPage(content_area)
        _set(page_inst.build(page))

    def show_activitePedagogique(e=None):
        page_inst = ActivitepedagogiquePage(content_area)
        _set(page_inst.build(page))

    def show_attempts(e=None):
        page_inst = AttemptsPage(content_area)
        _set(page_inst.build(page))

    def show_comparaison(e=None):
        page_inst = ComparaisonPage(content_area)
        _set(page_inst.build(page))

    def show_exerciseEngine(e=None):
        page_inst = ExerciseenginePage(content_area)
        _set(page_inst.build(page))

    def show_learners(e=None):
        page_inst = LearnersPage(content_area)
        _set(page_inst.build(page))

    def show_navigation(e=None):
        page_inst = NavigationPage(content_area)
        _set(page_inst.build(page))

    def show_ontologies(e=None):
        page_inst = OntologiesPage(content_area)
        _set(page_inst.build(page))

    def show_promptFabricationAAV(e=None):
        page_inst = PromptfabricationaavPage(content_area)
        _set(page_inst.build(page))

    def show_remediation(e=None):
        page_inst = RemediationPage(content_area)
        _set(page_inst.build(page))

    def show_reports(e=None):
        page_inst = ReportsPage(content_area)
        _set(page_inst.build(page))

    def show_statuts(e=None):
        page_inst = StatutsPage(content_area)
        _set(page_inst.build(page))

    def show_types(e=None):
        page_inst = TypesPage(content_area)
        _set(page_inst.build(page))

    def show_alerts(e=None):
        alerts_page = AlertsPage(content_area, show_details, show_about)
        _set(alerts_page.build(page))

    def show_about(e=None):
        about_page = AboutPage(content_area, show_alerts)
        _set(about_page.build(page))

    def show_details(aav_id):
        # On utilise la vue searchable par défaut si disponible
        if _HAS_AAV_GRAPH:
            _set(build_aav_graph_view(page, initial_id=aav_id))
        else:
            # Fallback vers la classe standard si le module graph n'est pas là
            details_page = DetailsPage(content_area, show_alerts)
            _set(details_page.build(aav_id, page))

    # ── Graph Views ─────────────────────────────────────────────────────────

    def show_aav_detail_view(e=None):
        if _HAS_AAV_GRAPH:
            # Nouvelle vue searchable (sans ID forcé)
            _set(build_aav_graph_view(page))
        else:
            # Fallback vers la vue de base si le module est absent
            _set(_unavailable_view("AAV Détail (Graph)", "aav_graph_view.py"))

    def show_dashboard_graph(e=None):
        if _HAS_DASHBOARD_GRAPH:
            _set(create_dashboard_view(page))
        else:
            _set(_unavailable_view("Dashboard (Graph)", "dashboard_view.py"))

    def show_metrics_graph(e=None):
        if _HAS_METRICS_GRAPH:
            _set(create_metrics_view(page))
        else:
            _set(_unavailable_view("Métriques (Graph)", "metrics_view.py"))

    def show_sessions_graph(e=None):
        if _HAS_SESSIONS_GRAPH:
            _set(build_session_view(page))
        else:
            _set(_unavailable_view("Sessions (Graph)", "session.py"))

    # ── Sidebar ───────────────────────────────────────────────────────────────
    sidebar = Sidebar(
        show_alerts_cb     = show_alerts,
        show_about_cb      = show_about,
        show_aav_detail_cb = show_aav_detail_view,
        show_dashboard_cb  = show_dashboard_graph,
        show_metrics_cb    = show_metrics_graph,
        show_sessions_cb   = show_sessions_graph,
        show_aavs_cb = show_aavs,
        show_activitePedagogique_cb = show_activitePedagogique,
        show_attempts_cb = show_attempts,
        show_comparaison_cb = show_comparaison,
        show_exerciseEngine_cb = show_exerciseEngine,
        show_learners_cb = show_learners,
        show_navigation_cb = show_navigation,
        show_ontologies_cb = show_ontologies,
        show_promptFabricationAAV_cb = show_promptFabricationAAV,
        show_remediation_cb = show_remediation,
        show_reports_cb = show_reports,
        show_statuts_cb = show_statuts,
        show_types_cb = show_types,
        show_dashboard_page_cb = show_dashboard_page,
        show_sessions_page_cb = show_sessions_page
    )
    sidebar_ui = sidebar.build()

    # ── Layout ────────────────────────────────────────────────────────────────
    main_layout = ft.Row(
        [
            ft.Container(
                content=sidebar_ui,
                width=260,
                expand=False,
                bgcolor="#22223e",
                alignment=ft.Alignment(-1, -1),
            ),
            ft.VerticalDivider(width=1, color="#424242"),
            ft.Container(
                content=content_area,
                expand=True,
                padding=ft.padding.all(20),
            ),
        ],
        expand=True,
        spacing=0,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

    page.add(main_layout)
    show_about()


def _unavailable_view(name: str, filename: str) -> ft.Container:
    return ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=48, color="#FF9800"),
            ft.Text(f"Module « {name} » indisponible", size=20,
                    weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
            ft.Text(f"Vérifiez que {filename} est présent.",
                    size=13, color=ft.Colors.WHITE54),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
           alignment=ft.MainAxisAlignment.CENTER, spacing=12),
        expand=True,
        alignment=ft.Alignment(0, 0),
    )


if __name__ == "__main__":
    ft.app(main)