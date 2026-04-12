"""Metrics Page - View quality metrics for AAVs"""

import flet as ft
import requests

class MetricsPage(ft.UserControl):
    def __init__(self, api_url: str):
        super().__init__()
        self.api_url = api_url
        self.metrics = []
        self.load_metrics()
        
    def load_metrics(self):
        """Load metrics from API"""
        try:
            response = requests.get(f"{self.api_url}/metrics/aav/")
            if response.status_code == 200:
                self.metrics = response.json()
        except Exception as e:
            print(f"Error loading metrics: {e}")
    
    def build(self):
        """Build metrics page UI"""
        content = ft.Column(
            [
                # Header
                self.build_header(),
                ft.Divider(height=15),
                
                # Metrics list
                ft.Text("📊 Quality Metrics", size=18, weight="bold", color="#1F1F1F"),
                self.build_metrics_table(),
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
                ft.TextField(
                    label="🔍 Search metrics",
                    width=300,
                    prefix_icon=ft.icons.SEARCH,
                    border_radius=8,
                ),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "🔄 Calculate All",
                    icon=ft.icons.REFRESH,
                    color="white",
                    bgcolor="#1976D2",
                ),
                ft.IconButton(
                    ft.icons.REFRESH,
                    icon_color="#2E7D32",
                    tooltip="Refresh"
                ),
            ]
        )
    
    def build_metrics_table(self):
        """Build metrics visualization"""
        if not self.metrics:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(name=ft.icons.INFO, size=64, color="#BDBDBD"),
                        ft.Text("No metrics calculated yet", size=16, color="#999999"),
                        ft.Text("Click 'Calculate All' to compute metrics", size=12, color="#BDBDBD"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                ),
                alignment=ft.alignment.center,
                expand=True,
                height=300
            )
        
        items = []
        for metric in self.metrics:
            # Get status color based on success rate
            success_rate = metric.get('taux_succes_moyen', 0)
            if success_rate >= 80:
                status_color = "#4CAF50"
                status_icon = "✅"
            elif success_rate >= 60:
                status_color = "#FFC107"
                status_icon = "⚠️"
            else:
                status_color = "#F44336"
                status_icon = "❌"
            
            item = ft.Container(
                content=ft.Column(
                    [
                        # Header row
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(
                                            f"AAV #{metric.get('id_aav', 'N/A')}",
                                            size=13,
                                            weight="bold",
                                            color="#1F1F1F"
                                        ),
                                    ],
                                    expand=True
                                ),
                                ft.Row(
                                    [
                                        ft.Text(
                                            f"Success: {success_rate:.1f}%",
                                            size=12,
                                            weight="bold",
                                            color=status_color
                                        ),
                                        ft.Icon(
                                            name=ft.icons.TRENDING_UP if success_rate >= 60 else ft.icons.TRENDING_DOWN,
                                            size=18,
                                            color=status_color
                                        ),
                                    ],
                                    spacing=5
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        
                        # Metrics details grid
                        ft.Row(
                            [
                                self.build_metric_card(
                                    "Coverage",
                                    f"{metric.get('score_covering_ressources', 0):.1f}%",
                                    "#1976D2"
                                ),
                                self.build_metric_card(
                                    "Attempts",
                                    str(metric.get('nb_tentatives_total', 0)),
                                    "#2E7D32"
                                ),
                                self.build_metric_card(
                                    "Learners",
                                    str(metric.get('nb_apprenants_distincts', 0)),
                                    "#F57C00"
                                ),
                                self.build_metric_card(
                                    "Deviation",
                                    f"{metric.get('ecart_type_scores', 0):.2f}",
                                    "#7B1FA2"
                                ),
                            ],
                            spacing=10
                        ),
                        
                        # Progress bar
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text("Success Rate", size=10, color="#666666"),
                                        ft.Text(f"{success_rate:.1f}%", size=10, weight="bold", color=status_color),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                ),
                                ft.ProgressBar(
                                    value=success_rate / 100,
                                    color=status_color,
                                    bgcolor="#E0E0E0",
                                    height=8,
                                    border_radius=4
                                ),
                            ],
                            spacing=5,
                            width=300
                        ),
                    ],
                    spacing=12
                ),
                padding=15,
                bgcolor="white",
                border_radius=8,
                border=ft.border.all(1, "#E0E0E0"),
                margin=ft.margin.only(bottom=10)
            )
            items.append(item)
        
        return ft.Column(items, spacing=0, scroll=ft.ScrollMode.AUTO)
    
    def build_metric_card(self, label: str, value: str, color: str):
        """Build individual metric card"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(label, size=10, color="#999999"),
                    ft.Text(value, size=14, weight="bold", color=color),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4
            ),
            padding=10,
            bgcolor=f"{color}10",
            border_radius=6,
            expand=True,
            border=ft.border.all(1, f"{color}30")
        )
