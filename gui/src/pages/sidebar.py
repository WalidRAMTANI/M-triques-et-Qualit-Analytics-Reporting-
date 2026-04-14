"""
Sidebar navigation component for AAV Dashboard GUI.

Provides main navigation buttons and project information display.
"""

import sys
from pathlib import Path
import flet as ft

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class Sidebar:
    """Sidebar component with navigation buttons and project info."""
    
    def __init__(
        self,
        show_alerts_cb,
        show_about_cb,
        show_aav_detail_cb=None,
        show_dashboard_cb=None,
        show_metrics_cb=None,
        show_sessions_cb=None,
    ):
        self.show_alerts = show_alerts_cb
        self.show_about = show_about_cb
        self.show_aav_detail = show_aav_detail_cb
        self.show_dashboard = show_dashboard_cb
        self.show_metrics = show_metrics_cb
        self.show_sessions = show_sessions_cb
        self.sidebar_content = None
    
    def build(self):
        """
        Build and return the sidebar UI component.
        
        Constructs a vertical sidebar with:
        - Project logo/title section
        - Navigation buttons (Alerts, About)
        - Project description
        
        Returns:
            ft.Container: Styled sidebar container with navigation and info
        
        Side Effects:
            None
        """
        self.sidebar_content = ft.Container(
            content=ft.Column(
                [
                    # Header Section
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.Icons.DASHBOARD, size=40, color="#9C27B0"),
                                ft.Text(
                                    "AAV Dashboard",
                                    size=18,
                                    weight=ft.FontWeight.W_700,
                                    color="#FFFFFF",
                                ),
                                ft.Text(
                                    "v1.0",
                                    size=10,
                                    color="#BDBDBD",
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        bgcolor="#4A148C",
                        border_radius=10,
                        padding=16,
                        margin=ft.margin.only(bottom=20),
                    ),
                    
                    # Navigation Buttons Section
                    ft.Text(
                        "Navigation",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color="#E0E0E0",
                    ),
                    
                    ft.ElevatedButton(
                        content=ft.Row([ft.Icon(ft.Icons.WARNING, size=20), ft.Text("Alerts", expand=True)], spacing=10),
                        on_click=self.show_alerts,
                        style=ft.ButtonStyle(color="#FFFFFF", bgcolor={ft.ControlState.DEFAULT: "#B71C1C"}),
                        width=200,
                    ),
                    
                    ft.ElevatedButton(
                        content=ft.Row([ft.Icon(ft.Icons.ANALYTICS, size=20), ft.Text("AAV Detail", expand=True)], spacing=10),
                        on_click=self.show_aav_detail,
                        style=ft.ButtonStyle(color="#FFFFFF", bgcolor={ft.ControlState.DEFAULT: "#4A148C"}),
                        width=200,
                    ),
                    
                    ft.ElevatedButton(
                        content=ft.Row([ft.Icon(ft.Icons.DASHBOARD_CUSTOMIZE, size=20), ft.Text("Dashboard", expand=True)], spacing=10),
                        on_click=self.show_dashboard,
                        style=ft.ButtonStyle(color="#FFFFFF", bgcolor={ft.ControlState.DEFAULT: "#1565C0"}),
                        width=200,
                    ),
                    
                    ft.ElevatedButton(
                        content=ft.Row([ft.Icon(ft.Icons.BAR_CHART, size=20), ft.Text("Metrics", expand=True)], spacing=10),
                        on_click=self.show_metrics,
                        style=ft.ButtonStyle(color="#FFFFFF", bgcolor={ft.ControlState.DEFAULT: "#00695C"}),
                        width=200,
                    ),
                    
                    ft.ElevatedButton(
                        content=ft.Row([ft.Icon(ft.Icons.TIMER, size=20), ft.Text("Sessions", expand=True)], spacing=10),
                        on_click=self.show_sessions,
                        style=ft.ButtonStyle(color="#FFFFFF", bgcolor={ft.ControlState.DEFAULT: "#E65100"}),
                        width=200,
                    ),
                    
                    ft.ElevatedButton(
                        content=ft.Row([ft.Icon(ft.Icons.INFO, size=20), ft.Text("About", expand=True)], spacing=10),
                        on_click=self.show_about,
                        style=ft.ButtonStyle(color="#FFFFFF", bgcolor={ft.ControlState.DEFAULT: "#37474F"}),
                        width=200,
                    ),
                    
                    ft.Divider(height=20),
                    
                    # Project Info Section
                    ft.Text(
                        "About Project",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color="#E0E0E0",
                    ),
                    
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "AAV Monitoring System",
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                    color="#FFFFFF",
                                ),
                                ft.Text(
                                    "Comprehensive dashboard for monitoring "
                                    "Learning Activities (AAV) across the platform. "
                                    "Track difficult, unused, and fragile activities. "
                                    "Identify students at risk and analyze performance metrics.",
                                    size=11,
                                    color="#E0E0E0",
                                    selectable=True,
                                ),
                            ],
                            spacing=8,
                        ),
                        bgcolor="#2a2a3e",
                        border_radius=8,
                        padding=12,
                    ),
                    
                    ft.Divider(height=20),
                    
                    # Features Section
                    ft.Text(
                        "Features",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color="#E0E0E0",
                    ),
                    
                    *self._build_feature_list(),
                ],
                spacing=12,
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=16,
        )
        
        return self.sidebar_content
    
    def _build_feature_list(self):
        """
        Build feature list items for sidebar display.
        
        Creates a list of feature badge containers showing main capabilities
        of the AAV Dashboard system.
        
        Returns:
            list of ft.Container: Feature badge containers
        
        Side Effects:
            None
        """
        features = [
            "📊 Alert Metrics",
            "⚠️ Risk Detection",
            "🔍 AAV Search",
            "📈 Analytics",
        ]
        
        return [
            ft.Container(
                content=ft.Text(
                    feature,
                    size=10,
                    color="#E0E0E0",
                ),
                bgcolor="#2a2a3e",
                border_radius=6,
                padding=ft.padding.symmetric(horizontal=8, vertical=6),
            )
            for feature in features
        ]
