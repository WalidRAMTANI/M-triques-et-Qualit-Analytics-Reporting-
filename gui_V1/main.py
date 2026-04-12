"""
Quality Metrics & Analytics Platform - Flet GUI Application
Modern desktop application for monitoring AAV (Learning Outcomes) metrics
"""

import flet as ft
import requests
from datetime import datetime
from pages.home import HomePage
from pages.aavs import AAVsPage
from pages.metrics import MetricsPage
from pages.alerts import AlertsPage
from pages.comparison import ComparisonPage
from pages.reports import ReportsPage
from pages.settings import SettingsPage

# API Configuration
API_URL = "http://localhost:8000"

class QualityMetricsApp:
    def __init__(self):
        self.current_page = None
        self.api_url = API_URL
        self.theme_mode = ft.ThemeMode.LIGHT
        
    def build(self, page: ft.Page):
        """Build the main application"""
        page.title = "📊 Quality Metrics & Analytics"
        page.window.min_width = 1000
        page.window.min_height = 700
        page.window.width = 1400
        page.window.height = 900
        page.padding = 0
        page.spacing = 0
        
        # Set theme
        page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary="#2E7D32",  # Green
                secondary="#1976D2",  # Blue
                tertiary="#F57C00",  # Orange
                error="#D32F2F"  # Red
            )
        )
        
        # Initialize pages
        self.pages = {
            'home': HomePage(self.api_url),
            'aavs': AAVsPage(self.api_url),
            'metrics': MetricsPage(self.api_url),
            'alerts': AlertsPage(self.api_url),
            'comparison': ComparisonPage(self.api_url),
            'reports': ReportsPage(self.api_url),
            'settings': SettingsPage(self.api_url),
        }
        
        # Navigation rail
        self.nav_rail = self.create_navigation()
        
        # Main content area
        self.content_area = ft.Container(
            content=self.pages['home'],
            expand=True,
            bgcolor="#F5F5F5"
        )
        
        # Header
        header = self.create_header()
        
        # Main layout
        main_layout = ft.Row(
            [
                self.nav_rail,
                ft.VerticalDivider(width=1),
                ft.Column(
                    [
                        header,
                        ft.Divider(height=1),
                        self.content_area
                    ],
                    expand=True,
                    spacing=0
                )
            ],
            expand=True,
            spacing=0
        )
        
        page.add(main_layout)
        self.page = page
        
    def create_header(self):
        """Create top header with title and status"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(name=ft.icons.DASHBOARD, size=28, color="#2E7D32"),
                    ft.Text(
                        "Quality Metrics & Analytics Platform",
                        size=20,
                        weight="bold",
                        color="#1F1F1F"
                    ),
                    ft.Container(expand=True),
                    ft.Icon(name=ft.icons.CHECK_CIRCLE, size=20, color="#4CAF50"),
                    ft.Text(
                        "Connected",
                        size=12,
                        color="#4CAF50"
                    ),
                    ft.Text(
                        datetime.now().strftime("%d/%m/%Y %H:%M"),
                        size=12,
                        color="#666666"
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=15,
            bgcolor="white",
            border_radius=0
        )
        
    def create_navigation(self):
        """Create navigation rail"""
        nav_items = [
            ("home", ft.icons.HOME, "Dashboard"),
            ("aavs", ft.icons.SCHOOL, "AAVs"),
            ("metrics", ft.icons.SHOW_CHART, "Metrics"),
            ("alerts", ft.icons.WARNING, "Alerts"),
            ("comparison", ft.icons.COMPARE_ARROWS, "Compare"),
            ("reports", ft.icons.DESCRIPTION, "Reports"),
            ("settings", ft.icons.SETTINGS, "Settings"),
        ]
        
        def nav_click(e, page_name):
            self.content_area.content = self.pages[page_name]
            self.content_area.update()
            # Update nav rail selection
            for item in nav_rail.destinations:
                if item.key == page_name:
                    item.selected = True
                else:
                    item.selected = False
            nav_rail.update()
        
        destinations = []
        for key, icon, label in nav_items:
            destinations.append(
                ft.NavigationRailDestination(
                    icon=icon,
                    selected_icon=icon,
                    label=label
                )
            )
        
        nav_rail = ft.NavigationRail(
            selected_index=0,
            destinations=destinations,
            on_change=lambda e: nav_click(e, list(self.pages.keys())[e.control.selected_index]),
            bgcolor="#FFFFFF",
            indicator_color="#2E7D32",
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=80,
            min_extended_width=180,
        )
        
        return nav_rail

def main(page: ft.Page):
    """Entry point"""
    app = QualityMetricsApp()
    app.build(page)

if __name__ == "__main__":
    ft.app(target=main)
