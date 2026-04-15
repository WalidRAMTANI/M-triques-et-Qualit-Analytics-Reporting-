import sys
import flet as ft
from pathlib import Path

# Configuration du chemin racine pour les imports internes
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Imports des composants de l'application centralises
from pages import (
    AboutPage, DetailsPage, AavsPage, ActivitepedagogiquePage, AdminPage,
    AlertsPage, AttemptsPage, ComparaisonPage, DashboardPage,
    ExerciseenginePage, LearnersPage, NavigationPage, OntologiesPage,
    PromptfabricationaavPage, RemediationPage, ReportsPage, SessionsPage,
    Sidebar, StatutsPage, TypesPage
)

# Tentatives d'imports des modules de visualisation graphique (dashboards complexes)
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
except Exception:
    _HAS_AAV_GRAPH = False

try:
    from session import build_session_view
    _HAS_SESSIONS_GRAPH = True
except Exception:
    _HAS_SESSIONS_GRAPH = False


def _unavailable_view(name: str, filename: str) -> ft.Container:
    """Affiche une vue de remplacement lorsqu'un module graphique est manquant."""
    return ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.ERROR_OUTLINE, color="#F44336", size=50),
            ft.Text(f"Vue '{name}' non disponible", size=20, weight="bold", color="#F44336"),
            ft.Text(f"Le module '{filename}' n'a pas pu être chargé (absent ou erreur d'import).", size=14),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        alignment=ft.alignment.center, expand=True
    )

def main(page: ft.Page):
    """
    Point d'entrée principal de l'application Flet.
    Gère la navigation, les permissions professeur et l'affichage des pages.
    """
    page.title = "AAV Dashboard"
    page.bgcolor = "#1a1a2e"
    page.theme = ft.Theme(color_scheme_seed="#9C27B0")
    page.window.width = 1200
    page.window.height = 800
    page.padding = 0

    # Initialisation de l'état utilisateur (Mode Eleve par défaut)
    if page.session.get("is_professor") is None:
        page.session.set("is_professor", False)

    content_area = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

    def _set(view_control):
        """Met à jour le contenu principal de la page."""
        content_area.controls.clear()
        content_area.controls.append(view_control)
        page.update()

    # Callbacks de navigation
    def show_aavs(e=None):
        inst = AavsPage(content_area, is_professor=page.session.get("is_professor"))
        _set(inst.build(page))

    def show_dashboard_page(e=None):
        inst = DashboardPage(content_area)
        _set(inst.build(page))

    def show_sessions_page(e=None):
        inst = SessionsPage(content_area, is_professor=page.session.get("is_professor"))
        _set(inst.build(page))

    def show_activitePedagogique(e=None):
        inst = ActivitepedagogiquePage(content_area, is_professor=page.session.get("is_professor"))
        _set(inst.build(page))

    def show_attempts(e=None):
        inst = AttemptsPage(content_area, is_professor=page.session.get("is_professor"))
        _set(inst.build(page))

    def show_comparaison(e=None):
        _set(ComparaisonPage(content_area).build(page))

    def show_exerciseEngine(e=None):
        _set(ExerciseenginePage(content_area).build(page))

    def show_learners(e=None):
        inst = LearnersPage(content_area, is_professor=page.session.get("is_professor"))
        _set(inst.build(page))

    def show_navigation(e=None):
        _set(NavigationPage(content_area).build(page))

    def show_ontologies(e=None):
        inst = OntologiesPage(content_area, is_professor=page.session.get("is_professor"))
        _set(inst.build(page))

    def show_promptFabricationAAV(e=None):
        _set(PromptfabricationaavPage(content_area).build(page))

    def show_remediation(e=None):
        _set(RemediationPage(content_area).build(page))

    def show_reports(e=None):
        _set(ReportsPage(content_area).build(page))

    def show_statuts(e=None):
        _set(StatutsPage(content_area).build(page))

    def show_types(e=None):
        _set(TypesPage(content_area).build(page))

    def show_alerts(e=None):
        _set(AlertsPage(content_area, show_details, show_about).build(page))

    def show_about(e=None):
        _set(AboutPage(content_area, show_alerts).build(page))

    def show_admin(e=None):
        def on_success():
            page.session.set("is_professor", True)
            sidebar.update_role(True)
            show_dashboard_graph()
            page.snack_bar = ft.SnackBar(ft.Text("Mode Professeur active"), bgcolor="green")
            page.snack_bar.open = True
            page.update()

        def on_logout():
            page.session.set("is_professor", False)
            sidebar.update_role(False)
            show_about()
            page.snack_bar = ft.SnackBar(ft.Text("Mode Eleve active"), bgcolor="#1565C0")
            page.snack_bar.open = True
            page.update()

        _set(AdminPage(content_area, on_success, on_logout, is_professor=page.session.get("is_professor")).build(page))

    def show_details(aav_id):
        if _HAS_AAV_GRAPH:
            _set(build_aav_graph_view(page, initial_id=aav_id))
        else:
            _set(DetailsPage(content_area, show_alerts).build(aav_id, page))

    def show_aav_detail_view(e=None):
        if _HAS_AAV_GRAPH:
            _set(build_aav_graph_view(page))
        else:
            _set(_unavailable_view("AAV Detail (Graph)", "aav_graph_view.py"))

    def show_dashboard_graph(e=None):
        if _HAS_DASHBOARD_GRAPH:
            _set(create_dashboard_view(page))
        else:
            _set(_unavailable_view("Dashboard (Graph)", "dashboard_view.py"))

    def show_metrics_graph(e=None):
        if _HAS_METRICS_GRAPH:
            _set(create_metrics_view(page))
        else:
            _set(_unavailable_view("Metriques (Graph)", "metrics_view.py"))

    def show_sessions_graph(e=None):
        if _HAS_SESSIONS_GRAPH:
            _set(build_session_view(page))
        else:
            _set(_unavailable_view("Sessions (Graph)", "session.py"))

    # Initialisation de la barre de navigation latérale
    sidebar = Sidebar(
        show_alerts_cb=show_alerts,
        show_about_cb=show_about,
        show_aav_detail_cb=show_aav_detail_view,
        show_dashboard_cb=show_dashboard_graph,
        show_metrics_cb=show_metrics_graph,
        show_sessions_cb=show_sessions_graph,
        show_aavs_cb=show_aavs,
        show_activitePedagogique_cb=show_activitePedagogique,
        show_attempts_cb=show_attempts,
        show_comparaison_cb=show_comparaison,
        show_exerciseEngine_cb=show_exerciseEngine,
        show_learners_cb=show_learners,
        show_navigation_cb=show_navigation,
        show_ontologies_cb=show_ontologies,
        show_promptFabricationAAV_cb=show_promptFabricationAAV,
        show_remediation_cb=show_remediation,
        show_reports_cb=show_reports,
        show_statuts_cb=show_statuts,
        show_types_cb=show_types,
        show_dashboard_page_cb=show_dashboard_page,
        show_sessions_page_cb=show_sessions_page,
        show_admin_cb=show_admin,
        is_professor=page.session.get("is_professor")
    )
    sidebar_ui = sidebar.build()

    main_layout = ft.Row(
        [
            ft.Container(content=sidebar_ui, width=260, bgcolor="#22223e", alignment=ft.Alignment(-1, -1)),
            ft.VerticalDivider(width=1, color="#424242"),
            ft.Container(content=content_area, expand=True, padding=ft.padding.all(20)),
        ],
        expand=True, spacing=0, vertical_alignment=ft.CrossAxisAlignment.START,
    )
    page.add(main_layout)

if __name__ == "__main__":
    ft.app(main)