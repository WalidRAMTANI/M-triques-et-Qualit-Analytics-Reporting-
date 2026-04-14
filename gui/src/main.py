import sys
from pathlib import Path

# Add project root (projet_python) to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import flet as ft
from pages import AlertsPage, DetailsPage, Sidebar, AboutPage

# ── Import optional standalone view builders ──────────────────────────────────
# Each view lives in its own file; we import defensively so the app still
# runs even if a module has missing dependencies at dev time.
try:
    from dashboard_view import create_dashboard_view
    _HAS_DASHBOARD = True
except Exception:
    _HAS_DASHBOARD = False

try:
    from metrics_view import create_metrics_view
    _HAS_METRICS = True
except Exception:
    _HAS_METRICS = False

try:
    from aav_detail_page import build_aav_detail_view
    _HAS_AAV_DETAIL = True
except Exception:
    _HAS_AAV_DETAIL = False

try:
    from session import build_session_view
    _HAS_SESSIONS = True
except Exception:
    _HAS_SESSIONS = False


# ─────────────────────────────────────────────────────────────────────────────

def main(page: ft.Page):
    """
    Main application entry point for the AAV Dashboard GUI.

    Wires the Sidebar navigation to every available page:
      • Alertes          – AlertsPage  (alert_page / pages.py)
      • Détail AAV       – aav_detail_page.py
      • Tableau de Bord  – dashboard_view.py
      • Métriques        – metrics_view.py
      • Sessions         – session.py
      • À propos         – AboutPage (pages.py)
    """
    page.title   = "AAV Dashboard"
    page.bgcolor = "#1a1a2e"
    page.theme   = ft.Theme(color_scheme_seed="#9C27B0")
    page.window.width  = 1050
    page.window.height = 720
    page.padding = 0

    # ── Content area ─────────────────────────────────────────────────────────
    content_area = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

    def _set(view_control):
        """Replace the content area with the given control."""
        content_area.controls.clear()
        content_area.controls.append(view_control)
        page.update()

    # ── Page callbacks ────────────────────────────────────────────────────────

    def show_alerts(e=None):
        alerts_page = AlertsPage(content_area, show_details, show_about)
        _set(alerts_page.build(page))

    def show_details(aav_id):
        details_page = DetailsPage(content_area, show_alerts)
        _set(details_page.build(aav_id, page))

    def show_about(e=None):
        about_page = AboutPage(content_area, show_alerts)
        _set(about_page.build(page))

    # ── Optional pages (gracefully disabled when module is unavailable) ───────

    def show_aav_detail(e=None):
        if _HAS_AAV_DETAIL:
            _set(build_aav_detail_view(page))
        else:
            _set(_unavailable_view("Détail AAV", "aav_detail_page.py"))

    def show_dashboard(e=None):
        if _HAS_DASHBOARD:
            _set(create_dashboard_view(page))
        else:
            _set(_unavailable_view("Tableau de Bord", "dashboard_view.py"))

    def show_metrics(e=None):
        if _HAS_METRICS:
            _set(create_metrics_view(page))
        else:
            _set(_unavailable_view("Métriques & Qualité", "metrics_view.py"))

    def show_sessions(e=None):
        if _HAS_SESSIONS:
            _set(build_session_view(page))
        else:
            _set(_unavailable_view("Sessions", "session.py"))

    # ── Sidebar ───────────────────────────────────────────────────────────────
    sidebar = Sidebar(
        show_alerts_cb     = show_alerts,
        show_about_cb      = show_about,
        show_aav_detail_cb = show_aav_detail,
        show_dashboard_cb  = show_dashboard,
        show_metrics_cb    = show_metrics,
        show_sessions_cb   = show_sessions,
    )
    sidebar_ui = sidebar.build()

    # ── Layout ────────────────────────────────────────────────────────────────
    main_layout = ft.Row(
        [
            ft.Container(
                content=sidebar_ui,
                width=240,
                expand=False,
                bgcolor="#22223e",
                alignment=ft.alignment.top_left,
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

    # Start on the About page
    show_about()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _unavailable_view(name: str, filename: str) -> ft.Container:
    """Placeholder shown when a view module could not be imported."""
    return ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=48, color="#FF9800"),
            ft.Text(f"Module « {name} » indisponible", size=20,
                    weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
            ft.Text(f"Vérifiez que {filename} et ses dépendances sont présents.",
                    size=13, color=ft.Colors.WHITE54),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
           alignment=ft.MainAxisAlignment.CENTER, spacing=12),
        expand=True,
        alignment=ft.alignment.center,
    )


if __name__ == "__main__":
    ft.app(main)