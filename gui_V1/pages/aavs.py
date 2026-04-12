"""AAVs Page - Browse and search all learning outcomes"""

import flet as ft
import requests

class AAVsPage(ft.UserControl):
    def __init__(self, api_url: str):
        super().__init__()
        self.api_url = api_url
        self.aavs = []
        self.filtered_aavs = []
        self.load_aavs()
        
    def load_aavs(self):
        """Load AAVs from API"""
        try:
            response = requests.get(f"{self.api_url}/aavs/")
            if response.status_code == 200:
                self.aavs = response.json()
                self.filtered_aavs = self.aavs
        except Exception as e:
            print(f"Error loading AAVs: {e}")
    
    def build(self):
        """Build AAVs page UI"""
        content = ft.Column(
            [
                # Header with search
                self.build_header(),
                ft.Divider(height=15),
                
                # AAVs list
                ft.Text("📚 All Learning Outcomes (AAVs)", size=18, weight="bold", color="#1F1F1F"),
                self.build_aavs_list(),
            ],
            expand=True,
            spacing=10,
            scroll=ft.ScrollMode.AUTO
        )
        return ft.Container(content=content, padding=20)
    
    def build_header(self):
        """Header with search and filters"""
        search_field = ft.TextField(
            label="🔍 Search AAVs",
            width=300,
            prefix_icon=ft.icons.SEARCH,
            border_radius=8,
        )
        
        return ft.Row(
            [
                search_field,
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "➕ Add AAV",
                    icon=ft.icons.ADD,
                    color="white",
                    bgcolor="#2E7D32",
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
    
    def build_aavs_list(self):
        """Build AAVs list view"""
        if not self.filtered_aavs:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(name=ft.icons.INFO, size=64, color="#BDBDBD"),
                        ft.Text("No AAVs found", size=16, color="#999999"),
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
        for aav in self.filtered_aavs:
            item = ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(
                                            aav.get('nom', 'Unknown'),
                                            size=14,
                                            weight="bold",
                                            color="#1F1F1F"
                                        ),
                                        ft.Text(
                                            aav.get('libelle_integration', ''),
                                            size=11,
                                            color="#666666"
                                        ),
                                    ],
                                    spacing=4,
                                    expand=True
                                ),
                                ft.Row(
                                    [
                                        ft.Chip(
                                            label=ft.Text(
                                                aav.get('discipline', 'N/A'),
                                                size=10
                                            ),
                                            bgcolor="#E8F5E9",
                                            label_style=ft.TextStyle(color="#2E7D32")
                                        ),
                                        ft.Chip(
                                            label=ft.Text(
                                                aav.get('enseignement', 'N/A'),
                                                size=10
                                            ),
                                            bgcolor="#E3F2FD",
                                            label_style=ft.TextStyle(color="#1976D2")
                                        ),
                                    ],
                                    spacing=8
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            spacing=15
                        ),
                        ft.Divider(height=10),
                        ft.Row(
                            [
                                ft.TextButton(
                                    "📊 View Metrics",
                                    icon=ft.icons.SHOW_CHART,
                                ),
                                ft.TextButton(
                                    "📈 History",
                                    icon=ft.icons.HISTORY,
                                ),
                                ft.TextButton(
                                    "✏️ Edit",
                                    icon=ft.icons.EDIT,
                                ),
                            ],
                            spacing=8
                        ),
                    ],
                    spacing=8
                ),
                padding=15,
                bgcolor="white",
                border_radius=8,
                border=ft.border.all(1, "#E0E0E0"),
                margin=ft.margin.only(bottom=10)
            )
            items.append(item)
        
        return ft.Column(items, spacing=0, scroll=ft.ScrollMode.AUTO)
