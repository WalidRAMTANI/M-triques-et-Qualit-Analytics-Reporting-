"""Settings Page - Configure app preferences"""

import flet as ft

class SettingsPage(ft.UserControl):
    def __init__(self, api_url: str):
        super().__init__()
        self.api_url = api_url
        
    def build(self):
        """Build settings page UI"""
        content = ft.Column(
            [
                ft.Text("⚙️ Settings", size=18, weight="bold", color="#1F1F1F"),
                ft.Divider(height=15),
                
                # API Configuration
                self.build_api_section(),
                ft.Divider(height=20),
                
                # Application Settings
                self.build_app_section(),
                ft.Divider(height=20),
                
                # Display Settings
                self.build_display_section(),
                ft.Divider(height=20),
                
                # About
                self.build_about_section(),
                
                ft.Container(expand=True),
            ],
            expand=True,
            spacing=10,
            scroll=ft.ScrollMode.AUTO
        )
        return ft.Container(content=content, padding=20)
    
    def build_settings_section(self, title: str, icon: str, content):
        """Build a settings section"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(icon, size=24),
                            ft.Text(title, size=14, weight="bold", color="#1F1F1F"),
                        ],
                        spacing=10
                    ),
                    ft.Divider(height=10),
                    content,
                ],
                spacing=10
            ),
            padding=15,
            bgcolor="white",
            border_radius=8,
            border=ft.border.all(1, "#E0E0E0")
        )
    
    def build_api_section(self):
        """API configuration section"""
        return self.build_settings_section(
            "API Configuration",
            "🔌",
            ft.Column(
                [
                    ft.TextField(
                        label="API URL",
                        value=self.api_url,
                        prefix_icon=ft.icons.LANGUAGE,
                        width=400,
                    ),
                    ft.TextField(
                        label="API Key (optional)",
                        password=True,
                        prefix_icon=ft.icons.VPN_KEY,
                        width=400,
                    ),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "🔍 Test Connection",
                                icon=ft.icons.LINK_OFF,
                                color="white",
                                bgcolor="#1976D2",
                            ),
                            ft.Text(
                                "Status: Connected ✅",
                                size=11,
                                color="#4CAF50"
                            ),
                        ],
                        spacing=10
                    ),
                ],
                spacing=12
            )
        )
    
    def build_app_section(self):
        """Application settings section"""
        return self.build_settings_section(
            "Application Settings",
            "📱",
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Auto-refresh metrics", size=12, color="#666666"),
                            ft.Container(expand=True),
                            ft.Switch(value=True),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Row(
                        [
                            ft.Text("Refresh interval (minutes)", size=12, color="#666666"),
                            ft.Container(expand=True),
                            ft.Dropdown(
                                width=100,
                                options=[
                                    ft.dropdown.Option("5"),
                                    ft.dropdown.Option("10"),
                                    ft.dropdown.Option("30"),
                                    ft.dropdown.Option("60"),
                                ],
                                value="10"
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Row(
                        [
                            ft.Text("Enable notifications", size=12, color="#666666"),
                            ft.Container(expand=True),
                            ft.Switch(value=True),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Row(
                        [
                            ft.Text("Show alerts on startup", size=12, color="#666666"),
                            ft.Container(expand=True),
                            ft.Switch(value=True),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                ],
                spacing=12
            )
        )
    
    def build_display_section(self):
        """Display settings section"""
        return self.build_settings_section(
            "Display Settings",
            "🎨",
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Theme", size=12, color="#666666"),
                            ft.Container(expand=True),
                            ft.Dropdown(
                                width=150,
                                options=[
                                    ft.dropdown.Option("Light"),
                                    ft.dropdown.Option("Dark"),
                                    ft.dropdown.Option("Auto"),
                                ],
                                value="Light"
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Row(
                        [
                            ft.Text("Font size", size=12, color="#666666"),
                            ft.Container(expand=True),
                            ft.Dropdown(
                                width=150,
                                options=[
                                    ft.dropdown.Option("Small"),
                                    ft.dropdown.Option("Normal"),
                                    ft.dropdown.Option("Large"),
                                ],
                                value="Normal"
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Row(
                        [
                            ft.Text("Show tooltips", size=12, color="#666666"),
                            ft.Container(expand=True),
                            ft.Switch(value=True),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                ],
                spacing=12
            )
        )
    
    def build_about_section(self):
        """About section"""
        return self.build_settings_section(
            "About",
            "ℹ️",
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Application", size=11, color="#666666", width=150),
                            ft.Text("Quality Metrics & Analytics", size=11, weight="bold", color="#1F1F1F"),
                        ],
                    ),
                    ft.Row(
                        [
                            ft.Text("Version", size=11, color="#666666", width=150),
                            ft.Text("1.0.0", size=11, weight="bold", color="#1F1F1F"),
                        ],
                    ),
                    ft.Row(
                        [
                            ft.Text("Built with", size=11, color="#666666", width=150),
                            ft.Text("Flet & FastAPI", size=11, weight="bold", color="#1F1F1F"),
                        ],
                    ),
                    ft.Row(
                        [
                            ft.Text("License", size=11, color="#666666", width=150),
                            ft.Text("MIT", size=11, weight="bold", color="#1F1F1F"),
                        ],
                    ),
                    ft.Divider(height=15),
                    ft.Row(
                        [
                            ft.TextButton(
                                "📖 Documentation",
                                icon=ft.icons.OPEN_IN_NEW,
                            ),
                            ft.TextButton(
                                "🐛 Report Issue",
                                icon=ft.icons.BUG_REPORT,
                            ),
                            ft.TextButton(
                                "⭐ GitHub",
                                icon=ft.icons.CODE,
                            ),
                        ],
                        spacing=8
                    ),
                ],
                spacing=10
            )
        )
