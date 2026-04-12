"""Comparison Page - Compare metrics between AAVs"""

import flet as ft
import requests

class ComparisonPage(ft.UserControl):
    def __init__(self, api_url: str):
        super().__init__()
        self.api_url = api_url
        self.aavs = []
        self.comparison_data = None
        self.load_aavs()
        
    def load_aavs(self):
        """Load AAVs for selection"""
        try:
            response = requests.get(f"{self.api_url}/aavs/")
            if response.status_code == 200:
                self.aavs = response.json()
        except Exception as e:
            print(f"Error loading AAVs: {e}")
    
    def build(self):
        """Build comparison page UI"""
        content = ft.Column(
            [
                # Header with selection
                self.build_header(),
                ft.Divider(height=15),
                
                # Comparison results
                ft.Text("🔄 AAV Comparison", size=18, weight="bold", color="#1F1F1F"),
                self.build_comparison_view(),
            ],
            expand=True,
            spacing=10,
            scroll=ft.ScrollMode.AUTO
        )
        return ft.Container(content=content, padding=20)
    
    def build_header(self):
        """Header with AAV selection"""
        aav_options = [ft.dropdown.Option(str(aav.get('id_aav', i))) for i, aav in enumerate(self.aavs)]
        
        return ft.Row(
            [
                ft.Column(
                    [
                        ft.Text("Select First AAV", size=11, color="#666666"),
                        ft.Dropdown(
                            width=200,
                            options=aav_options if aav_options else [ft.dropdown.Option("No AAVs")],
                            value=str(self.aavs[0].get('id_aav', '1')) if self.aavs else "1"
                        ),
                    ],
                    spacing=5
                ),
                ft.Text("VS", size=16, weight="bold", color="#1976D2"),
                ft.Column(
                    [
                        ft.Text("Select Second AAV", size=11, color="#666666"),
                        ft.Dropdown(
                            width=200,
                            options=aav_options if aav_options else [ft.dropdown.Option("No AAVs")],
                            value=str(self.aavs[1].get('id_aav', '2')) if len(self.aavs) > 1 else "2"
                        ),
                    ],
                    spacing=5
                ),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "🔍 Compare",
                    icon=ft.icons.COMPARE_ARROWS,
                    color="white",
                    bgcolor="#7B1FA2",
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=20
        )
    
    def build_comparison_view(self):
        """Build comparison visualization"""
        metrics = [
            {'name': 'Success Rate', 'aav1': 75.5, 'aav2': 68.3, 'unit': '%'},
            {'name': 'Coverage', 'aav1': 85.0, 'aav2': 92.0, 'unit': '%'},
            {'name': 'Total Attempts', 'aav1': 145, 'aav2': 123, 'unit': ''},
            {'name': 'Active Learners', 'aav1': 42, 'aav2': 38, 'unit': ''},
            {'name': 'Score Deviation', 'aav1': 18.5, 'aav2': 22.1, 'unit': ''},
        ]
        
        items = []
        for metric in metrics:
            diff = metric['aav1'] - metric['aav2']
            diff_color = "#4CAF50" if diff > 0 else "#F44336" if diff < 0 else "#999999"
            diff_icon = "▲" if diff > 0 else "▼" if diff < 0 else "="
            
            item = ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    metric['name'],
                                    size=12,
                                    weight="bold",
                                    color="#1F1F1F"
                                ),
                                ft.Container(expand=True),
                                ft.Row(
                                    [
                                        ft.Text(
                                            f"{diff_icon} {abs(diff):.1f}",
                                            size=11,
                                            weight="bold",
                                            color=diff_color
                                        ),
                                    ]
                                ),
                            ]
                        ),
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text("AAV 1", size=9, color="#999999"),
                                        ft.Text(
                                            f"{metric['aav1']}{metric['unit']}",
                                            size=14,
                                            weight="bold",
                                            color="#1976D2"
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=2,
                                    expand=True
                                ),
                                ft.VerticalDivider(width=1),
                                ft.Column(
                                    [
                                        ft.Text("AAV 2", size=9, color="#999999"),
                                        ft.Text(
                                            f"{metric['aav2']}{metric['unit']}",
                                            size=14,
                                            weight="bold",
                                            color="#7B1FA2"
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=2,
                                    expand=True
                                ),
                            ],
                            spacing=0
                        ),
                    ],
                    spacing=10
                ),
                padding=15,
                bgcolor="white",
                border_radius=8,
                border=ft.border.all(1, "#E0E0E0"),
                margin=ft.margin.only(bottom=10)
            )
            items.append(item)
        
        return ft.Column(items, spacing=0, scroll=ft.ScrollMode.AUTO)
