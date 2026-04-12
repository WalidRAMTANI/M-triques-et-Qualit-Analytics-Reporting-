"""Reports Page - Generate and view reports"""

import flet as ft
import requests

class ReportsPage(ft.UserControl):
    def __init__(self, api_url: str):
        super().__init__()
        self.api_url = api_url
        self.reports = []
        self.load_reports()
        
    def load_reports(self):
        """Load reports from API"""
        try:
            response = requests.get(f"{self.api_url}/reports/global")
            if response.status_code == 200:
                data = response.json()
                self.reports = [data] if data else []
        except Exception as e:
            print(f"Error loading reports: {e}")
    
    def build(self):
        """Build reports page UI"""
        content = ft.Column(
            [
                # Header with generation options
                self.build_header(),
                ft.Divider(height=15),
                
                # Reports list
                ft.Text("📄 Generated Reports", size=18, weight="bold", color="#1F1F1F"),
                self.build_reports_list(),
            ],
            expand=True,
            spacing=10,
            scroll=ft.ScrollMode.AUTO
        )
        return ft.Container(content=content, padding=20)
    
    def build_header(self):
        """Header with report generation options"""
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Generate New Report", size=13, weight="bold"),
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            "➕ Generate",
                            icon=ft.icons.ADD,
                            color="white",
                            bgcolor="#2E7D32",
                        ),
                    ],
                ),
                ft.Divider(height=10),
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("Report Type", size=11, color="#666666"),
                                ft.Dropdown(
                                    width=200,
                                    options=[
                                        ft.dropdown.Option("Comprehensive"),
                                        ft.dropdown.Option("Quality Summary"),
                                        ft.dropdown.Option("Alerts Only"),
                                        ft.dropdown.Option("Learner Progress"),
                                    ],
                                    value="Comprehensive"
                                ),
                            ],
                            spacing=5
                        ),
                        ft.Column(
                            [
                                ft.Text("Format", size=11, color="#666666"),
                                ft.Dropdown(
                                    width=150,
                                    options=[
                                        ft.dropdown.Option("PDF"),
                                        ft.dropdown.Option("CSV"),
                                        ft.dropdown.Option("JSON"),
                                    ],
                                    value="PDF"
                                ),
                            ],
                            spacing=5
                        ),
                        ft.Column(
                            [
                                ft.Text("Time Period", size=11, color="#666666"),
                                ft.Dropdown(
                                    width=150,
                                    options=[
                                        ft.dropdown.Option("Last 7 days"),
                                        ft.dropdown.Option("Last 30 days"),
                                        ft.dropdown.Option("Last 90 days"),
                                        ft.dropdown.Option("All time"),
                                    ],
                                    value="Last 30 days"
                                ),
                            ],
                            spacing=5
                        ),
                    ],
                    spacing=20
                ),
            ],
            spacing=10,
            bgcolor="white",
            padding=15,
            border_radius=8,
            border=ft.border.all(1, "#E0E0E0")
        )
    
    def build_reports_list(self):
        """Build reports list view"""
        if not self.reports:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(name=ft.icons.NOTE_ADD, size=64, color="#BDBDBD"),
                        ft.Text("No reports generated yet", size=16, color="#999999"),
                        ft.Text("Use the form above to generate your first report", size=12, color="#BDBDBD"),
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
        for i, report in enumerate(self.reports, 1):
            item = ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(name=ft.icons.DESCRIPTION, size=28, color="#C62828"),
                                ft.Column(
                                    [
                                        ft.Text(
                                            f"Report #{i} - {report.get('titre', 'Comprehensive Report')}",
                                            size=13,
                                            weight="bold",
                                            color="#1F1F1F"
                                        ),
                                        ft.Text(
                                            f"Generated: {report.get('date_creation', 'N/A')}",
                                            size=10,
                                            color="#999999"
                                        ),
                                    ],
                                    expand=True,
                                    spacing=2
                                ),
                                ft.Row(
                                    [
                                        ft.Chip(
                                            label=ft.Text("PDF", size=10),
                                            bgcolor="#FFEBEE",
                                            label_style=ft.TextStyle(color="#C62828")
                                        ),
                                        ft.Chip(
                                            label=ft.Text(
                                                f"Size: {len(str(report).encode()) // 1024}KB",
                                                size=10
                                            ),
                                            bgcolor="#F3E5F5",
                                            label_style=ft.TextStyle(color="#6A1B9A")
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
                                    "📥 Download",
                                    icon=ft.icons.DOWNLOAD,
                                ),
                                ft.TextButton(
                                    "👁️ Preview",
                                    icon=ft.icons.PREVIEW,
                                ),
                                ft.TextButton(
                                    "🔗 Share",
                                    icon=ft.icons.SHARE,
                                ),
                                ft.TextButton(
                                    "🗑️ Delete",
                                    icon=ft.icons.DELETE,
                                ),
                            ],
                            spacing=8
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
