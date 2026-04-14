"""
About page for AAV Dashboard project information and documentation.

Displays project overview, features, technical stack, and contact information.
"""

import sys
from pathlib import Path
import flet as ft


class AboutPage:
    """About page displaying project information and features."""
    
    def __init__(self, content_area, show_alerts_callback):
        """
        Initialize the About Page.
        
        Args:
            content_area (ft.Column): Container for page content
            show_alerts_callback (callable): Callback function to navigate back to alerts page
        
        Returns:
            None
        """
        self.content_area = content_area
        self.show_alerts = show_alerts_callback
        self.page_content = None
    
    def build(self, page):
        """
        Build and return the about page UI.
        
        Constructs a comprehensive information page displaying:
        - Project title and version
        - Project description and objectives
        - Key features and capabilities
        - Technical stack and technologies
        - Screenshots/diagrams section
        - Contact and support information
        
        Args:
            page (ft.Page): The Flet page object for UI rendering
        
        Returns:
            ft.Column: Complete about page UI column with all project information
        
        Side Effects:
            None
        """
        self.page_content = ft.Column(
            [
                # Header
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(
                                    "AAV Dashboard",
                                    size=32,
                                    weight=ft.FontWeight.W_700,
                                ),
                                ft.Text(
                                    "Learning Activities Monitoring System - v1.0",
                                    color="#BDBDBD",
                                    size=14,
                                ),
                            ],
                            expand=True,
                        ),

                    ],
                    expand=True,
                ),
                
                ft.Divider(),
                
                # Project Overview
                self._build_section(
                    "📋 Project Overview",
                    "The AAV Dashboard is a comprehensive monitoring system designed to track "
                    "and analyze Learning Activities (AAV - Activités Académiques et Virtuelles) "
                    "across the educational platform. It provides real-time insights into activity "
                    "performance, identifies at-risk students, and helps educators optimize course "
                    "design and delivery.",
                ),
                
                # Objectives
                self._build_section(
                    "🎯 Objectives",
                    [
                        "✓ Monitor difficult, unused, and fragile learning activities",
                        "✓ Identify students at risk of academic failure",
                        "✓ Analyze activity success rates and engagement metrics",
                        "✓ Provide actionable insights for course improvement",
                        "✓ Enable data-driven educational decision making",
                    ],
                ),
                
                # Key Features
                self._build_section(
                    "⚡ Key Features",
                    [
                        "📊 Alert Dashboard: Real-time monitoring of activity status",
                        "⚠️ Risk Detection: Identify students struggling with specific AAVs",
                        "🔍 Detailed Analytics: Comprehensive AAV information and metadata",
                        "📈 Performance Metrics: Success rates, variance analysis",
                        "🎨 Intuitive UI: Clean, responsive interface for easy navigation",
                        "⚡ Fast Performance: Optimized API calls with error handling",
                    ],
                ),
                
                # Technical Stack
                self._build_section(
                    "🛠️ Technical Stack",
                    [
                        "Frontend: Flet (Python UI Framework) - Cross-platform GUI",
                        "Backend: FastAPI - Modern Python web framework",
                        "Database: SQLAlchemy ORM - Python SQL toolkit",
                        "HTTP Client: httpx - Async Python HTTP client",
                        "Language: Python 3.9+ - Modern, readable, maintainable",
                    ],
                ),
                
                # Architecture
                self._build_section(
                    "🏗️ Architecture",
                    [
                        "main.py: Application entry point and navigation orchestration",
                        "alert_page.py: Alerts dashboard displaying difficult/unused/fragile AAVs",
                        "aav_detail_page.py: Detailed view of individual AAVs",
                        "sidebar.py: Navigation sidebar with project information",
                        "utils.py: Shared utilities and API communication helpers",
                    ],
                ),
                
                # Data Flow
                self._build_section(
                    "🔄 Data Flow",
                    "User Interface (Flet) → Navigation Layer → API Client (httpx) → "
                    "FastAPI Backend → SQLAlchemy ORM → Database → Response Processing → "
                    "UI Update & Display",
                ),
                
                # Usage Instructions
                self._build_section(
                    "📖 Quick Start",
                    [
                        "1. Click 'Alerts' button to view the main dashboard",
                        "2. Review metrics for Difficult, Unused, and Fragile AAVs",
                        "3. Click on any AAV row to view detailed information",
                        "4. Enter an Ontology ID and click 'Search' to find students at risk",
                        "5. Color codes indicate: Green=Good Progress, Orange=Medium Risk, Red=High Risk",
                    ],
                ),
                
                # Performance Metrics
                self._build_section(
                    "📊 Performance Metrics",
                    [
                        "API Response Time: ~5 seconds (with timeout handling)",
                        "Supported Endpoints: 6+ REST API endpoints",
                        "Data Points: Difficulty, Success Rate, Variance Analysis",
                        "Student Risk Detection: Real-time progression tracking",
                        "Supported Ontology IDs: Dynamic search capability",
                    ],
                ),
                
                # Support & Contact
                self._build_section(
                    "📞 Support & Information",
                    [
                        "Project Repository: M-triques-et-Qualit-Analytics-Reporting",
                        "Owner: WalidRAMTANI",
                        "Branch: main",
                        "API Base: http://localhost:8000",
                        "For issues or feedback: Contact the development team",
                    ],
                ),
                
                ft.Divider(),
                
                # Footer
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "© 2026 Analytics Team - All Rights Reserved",
                                size=11,
                                color="#BDBDBD",
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "Built with Flet and Python",
                                size=10,
                                color="#424242",
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        spacing=4,
                    ),
                    alignment=ft.Alignment(0, 0),
                    padding=20,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=16,
        )
        
        return self.page_content
    
    def _build_section(self, title, content):
        """
        Build a formatted section container for about page.
        
        Creates a reusable section with title, divider, and content.
        Content can be a string or list of strings, automatically formatted.
        
        Args:
            title (str): Section heading with optional emoji prefix
            content (str or list of str): Section content. If list, displays each item
                on separate line. If string, displays as paragraph.
        
        Returns:
            ft.Container: Styled section container with background and padding
        
        Side Effects:
            None
        """
        content_controls = [
            ft.Text(
                title,
                size=14,
                weight=ft.FontWeight.W_600,
                color="#CE93D8",
            ),
            ft.Divider(height=1),
        ]
        
        if isinstance(content, list):
            for item in content:
                content_controls.append(
                    ft.Text(
                        item,
                        size=11,
                        color="#E0E0E0",
                        selectable=True,
                    )
                )
        else:
            content_controls.append(
                ft.Text(
                    content,
                    size=11,
                    color="#E0E0E0",
                    selectable=True,
                )
            )
        
        return ft.Container(
            content=ft.Column(content_controls, spacing=8),
            bgcolor="#2a2a3e",
            border_radius=10,
            padding=16,
        )
