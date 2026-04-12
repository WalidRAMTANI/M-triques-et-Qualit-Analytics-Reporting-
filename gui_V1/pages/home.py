"""Home Dashboard Page - Main overview with quick stats and navigation"""

import flet as ft
import requests
from datetime import datetime

class HomePage(ft.UserControl):
    def __init__(self, api_url: str):
        super().__init__()
        self.api_url = api_url
        self.stats = {
            'total_aavs': 0,
            'total_metrics': 0,
            'active_alerts': 0,
            'avg_success_rate': 0
        }
        self.load_stats()
        
    def load_stats(self):
        """Load statistics from API"""
        try:
            # Get AAVs count
            response = requests.get(f"{self.api_url}/aavs/")
            if response.status_code == 200:
                self.stats['total_aavs'] = len(response.json())
            
            # Get metrics count
            response = requests.get(f"{self.api_url}/metrics/aav/")
            if response.status_code == 200:
                metrics = response.json()
                self.stats['total_metrics'] = len(metrics)
                if metrics:
                    # Calculate average success rate
                    total_success = sum(m.get('taux_succes_moyen', 0) for m in metrics)
                    self.stats['avg_success_rate'] = total_success / len(metrics)
            
            # Get alerts count
            response = requests.get(f"{self.api_url}/alerts/")
            if response.status_code == 200:
                self.stats['active_alerts'] = len(response.json())
        except Exception as e:
            print(f"Error loading stats: {e}")
    
    def build(self):
        """Build home page UI"""
        content = ft.Column(
            [
                # Welcome section
                self.build_welcome_section(),
                
                ft.Divider(height=20),
                
                # Quick stats cards
                ft.Text("📊 Quick Statistics", size=18, weight="bold", color="#1F1F1F"),
                self.build_stats_section(),
                
                ft.Divider(height=20),
                
                # Navigation cards
                ft.Text("🧭 Quick Navigation", size=18, weight="bold", color="#1F1F1F"),
                self.build_navigation_cards(),
                
                ft.Container(expand=True),  # Spacer
                
                # Footer
                self.build_footer(),
            ],
            expand=True,
            spacing=10,
            scroll=ft.ScrollMode.AUTO
        )
        
        return ft.Container(
            content=content,
            padding=20
        )
    
    def build_welcome_section(self):
        """Welcome banner"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Welcome to Quality Metrics Dashboard",
                        size=24,
                        weight="bold",
                        color="white"
                    ),
                    ft.Text(
                        "Monitor, analyze and improve your AAV (Learning Outcomes) quality metrics",
                        size=14,
                        color="#E0E0E0"
                    ),
                ],
                spacing=5
            ),
            padding=20,
            bgcolor="#2E7D32",
            border_radius=10,
            shadow=ft.BoxShadow(blur_radius=5, color="#00000020")
        )
    
    def build_stats_section(self):
        """Statistics cards section"""
        stats_cards = [
            {
                'title': 'Total AAVs',
                'value': self.stats['total_aavs'],
                'icon': ft.icons.SCHOOL,
                'color': '#2E7D32',
                'light_bg': '#E8F5E9'
            },
            {
                'title': 'Calculated Metrics',
                'value': self.stats['total_metrics'],
                'icon': ft.icons.SHOW_CHART,
                'color': '#1976D2',
                'light_bg': '#E3F2FD'
            },
            {
                'title': 'Active Alerts',
                'value': self.stats['active_alerts'],
                'icon': ft.icons.WARNING,
                'color': '#F57C00',
                'light_bg': '#FFF3E0'
            },
            {
                'title': 'Avg Success Rate',
                'value': f"{self.stats['avg_success_rate']:.1f}%",
                'icon': ft.icons.TRENDING_UP,
                'color': '#D32F2F',
                'light_bg': '#FFEBEE'
            },
        ]
        
        cards = []
        for stat in stats_cards:
            card = ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(
                                    name=stat['icon'],
                                    size=32,
                                    color=stat['color']
                                ),
                                ft.Column(
                                    [
                                        ft.Text(
                                            stat['title'],
                                            size=12,
                                            color="#666666",
                                            weight="w500"
                                        ),
                                        ft.Text(
                                            str(stat['value']),
                                            size=24,
                                            weight="bold",
                                            color=stat['color']
                                        ),
                                    ],
                                    spacing=2
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            spacing=15
                        ),
                    ],
                    spacing=5
                ),
                padding=15,
                bgcolor=stat['light_bg'],
                border_radius=10,
                expand=True,
                shadow=ft.BoxShadow(blur_radius=3, color="#00000010")
            )
            cards.append(card)
        
        return ft.ResponsiveRow(cards, spacing=15, run_spacing=15)
    
    def build_navigation_cards(self):
        """Main navigation cards"""
        nav_items = [
            {
                'title': '🎓 Browse AAVs',
                'description': 'View and manage all learning outcomes',
                'icon': ft.icons.SCHOOL,
                'color': '#2E7D32'
            },
            {
                'title': '📈 View Metrics',
                'description': 'Quality metrics and performance indicators',
                'icon': ft.icons.SHOW_CHART,
                'color': '#1976D2'
            },
            {
                'title': '🚨 Monitor Alerts',
                'description': 'Problematic AAVs requiring attention',
                'icon': ft.icons.WARNING,
                'color': '#F57C00'
            },
            {
                'title': '🔄 Compare AAVs',
                'description': 'Compare metrics between different AAVs',
                'icon': ft.icons.COMPARE_ARROWS,
                'color': '#7B1FA2'
            },
            {
                'title': '📄 Generate Reports',
                'description': 'Create and download detailed reports',
                'icon': ft.icons.DESCRIPTION,
                'color': '#C62828'
            },
            {
                'title': '⚙️ Settings',
                'description': 'Configure app preferences and API',
                'icon': ft.icons.SETTINGS,
                'color': '#455A64'
            },
        ]
        
        cards = []
        for item in nav_items:
            card = ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(
                                    name=item['icon'],
                                    size=28,
                                    color=item['color']
                                ),
                                ft.Text(
                                    item['title'],
                                    size=14,
                                    weight="bold",
                                    color="#1F1F1F"
                                ),
                            ],
                            spacing=10,
                            alignment=ft.MainAxisAlignment.START
                        ),
                        ft.Text(
                            item['description'],
                            size=11,
                            color="#666666",
                            weight="w400"
                        ),
                    ],
                    spacing=8
                ),
                padding=15,
                bgcolor="white",
                border_radius=8,
                border=ft.border.all(1, "#E0E0E0"),
                expand=True,
                shadow=ft.BoxShadow(blur_radius=3, color="#00000010")
            )
            cards.append(card)
        
        return ft.ResponsiveRow(cards, spacing=15, run_spacing=15, columns=3)
    
    def build_footer(self):
        """Footer with version and info"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        "Quality Metrics v1.0.0",
                        size=11,
                        color="#999999"
                    ),
                    ft.Container(expand=True),
                    ft.Text(
                        f"Last updated: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                        size=11,
                        color="#999999"
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=ft.padding.only(top=15, bottom=5),
            border_radius=0
        )
