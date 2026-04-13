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
    
    def __init__(self, show_alerts_callback, show_about_callback):
        """
        Initialize the Sidebar.
        
        Args:
            show_alerts_callback (callable): Callback function to navigate to alerts page
            show_about_callback (callable): Callback function to display project info
        
        Returns:
            None
        """
        self.show_alerts = show_alerts_callback
        self.show_about = show_about_callback
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
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.WARNING, size=20),
                                ft.Text("Alerts", expand=True),
                            ],
                            spacing=10,
                        ),
                        on_click=self.show_alerts,
                        style=ft.ButtonStyle(
                            color="#FFFFFF",
                            bgcolor={ft.ControlState.DEFAULT: "#B71C1C"},
                        ),
                        width=200,
                    ),
                    
                    ft.ElevatedButton(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.INFO, size=20),
                                ft.Text("About", expand=True),
                            ],
                            spacing=10,
                        ),
                        on_click=self.show_about,
                        style=ft.ButtonStyle(
                            color="#FFFFFF",
                            bgcolor={ft.ControlState.DEFAULT: "#1565C0"},
                        ),
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
