"""Alerts Page - Monitor problematic AAVs"""

import flet as ft
import requests

class AlertsPage(ft.UserControl):
    def __init__(self, api_url: str):
        super().__init__()
        self.api_url = api_url
        self.alerts = []
        self.load_alerts()
        
    def load_alerts(self):
        """Load alerts from API"""
        try:
            response = requests.get(f"{self.api_url}/alerts/")
            if response.status_code == 200:
                self.alerts = response.json()
        except Exception as e:
            print(f"Error loading alerts: {e}")
    
    def build(self):
        """Build alerts page UI"""
        content = ft.Column(
            [
                # Header
                self.build_header(),
                ft.Divider(height=15),
                
                # Alerts list
                ft.Text("🚨 Quality Alerts", size=18, weight="bold", color="#1F1F1F"),
                self.build_alerts_list(),
            ],
            expand=True,
            spacing=10,
            scroll=ft.ScrollMode.AUTO
        )
        return ft.Container(content=content, padding=20)
    
    def build_header(self):
        """Header with filters"""
        return ft.Row(
            [
                ft.Dropdown(
                    label="Filter by type",
                    width=200,
                    options=[
                        ft.dropdown.Option("All"),
                        ft.dropdown.Option("Difficult"),
                        ft.dropdown.Option("Fragile"),
                        ft.dropdown.Option("Unused"),
                        ft.dropdown.Option("Blocking"),
                    ],
                    value="All"
                ),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "📊 Analyze",
                    icon=ft.icons.ANALYTICS,
                    color="white",
                    bgcolor="#F57C00",
                ),
            ]
        )
    
    def build_alerts_list(self):
        """Build alerts list view"""
        if not self.alerts:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(name=ft.icons.CHECK_CIRCLE, size=64, color="#4CAF50"),
                        ft.Text("No alerts detected", size=16, color="#4CAF50", weight="bold"),
                        ft.Text("All AAVs are performing well", size=12, color="#999999"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                ),
                alignment=ft.alignment.center,
                expand=True,
                height=300
            )
        
        alert_types = {
            'difficult': {'icon': '📉', 'color': '#D32F2F', 'label': 'Difficult'},
            'fragile': {'icon': '⚠️', 'color': '#F57C00', 'label': 'Fragile'},
            'unused': {'icon': '❌', 'color': '#757575', 'label': 'Unused'},
            'blocking': {'icon': '🚫', 'color': '#B71C1C', 'label': 'Blocking'},
        }
        
        items = []
        for alert in self.alerts:
            alert_type = alert.get('type_alerte', 'unknown').lower()
            alert_info = alert_types.get(alert_type, {'icon': 'ℹ️', 'color': '#1976D2', 'label': 'Info'})
            
            item = ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Text(alert_info['icon'], size=32),
                            width=50,
                            alignment=ft.alignment.center
                        ),
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(
                                            f"AAV #{alert.get('id_aav', 'N/A')}",
                                            size=13,
                                            weight="bold",
                                            color="#1F1F1F"
                                        ),
                                        ft.Chip(
                                            label=ft.Text(
                                                alert_info['label'],
                                                size=10,
                                                weight="bold"
                                            ),
                                            bgcolor=alert_info['color'],
                                            label_style=ft.TextStyle(color="white")
                                        ),
                                    ],
                                    spacing=10,
                                    alignment=ft.MainAxisAlignment.START
                                ),
                                ft.Text(
                                    alert.get('message', 'No description'),
                                    size=11,
                                    color="#666666",
                                    max_lines=2
                                ),
                                ft.Row(
                                    [
                                        ft.TextButton(
                                            "📊 View Details",
                                            icon=ft.icons.OPEN_IN_NEW,
                                        ),
                                        ft.TextButton(
                                            "✓ Dismiss",
                                            icon=ft.icons.CLOSE,
                                        ),
                                    ],
                                    spacing=8
                                ),
                            ],
                            expand=True,
                            spacing=6
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=15
                ),
                padding=15,
                bgcolor="white",
                border_radius=8,
                border=ft.border.all(2, alert_info['color']),
                margin=ft.margin.only(bottom=10)
            )
            items.append(item)
        
        return ft.Column(items, spacing=0, scroll=ft.ScrollMode.AUTO)
