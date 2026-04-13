"""
Alert Dashboard page for AAV monitoring.

Displays alerts for difficult, unused, and fragile AAVs,
and allows searching for students at risk.
"""

import sys
from pathlib import Path
import flet as ft

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import fetch, row, section, ALERTS_API


class AlertsPage:
    """Alert Dashboard page showing difficult, unused, and fragile AAVs."""
    
    def __init__(self, content_area, show_details_callback, show_about_callback):
        """
        Initialize the Alerts Page.
        
        Args:
            content_area (ft.Column): Container for page content
            show_details_callback (callable): Callback function to navigate to AAV details page
            show_about_callback (callable): Callback function to navigate back to about page
        
        Returns:
            None
        """
        self.content_area = content_area
        self.show_details = show_details_callback
        self.show_about = show_about_callback
        self.onto_field = ft.TextField(label="Ontologie ID", width=200, dense=True)
        self.risk_col = ft.Column()
        self.page_content = None
    
    def load_risk(self, e=None):
        """
        Load and display students at risk for the given ontology ID.
        
        Fetches student data from the API for a specific ontology ID and populates
        the risk column with learner information including name, progression percentage,
        and number of blocked AAVs. Color-codes progression based on thresholds.
        
        Args:
            e (ft.ControlEvent, optional): Event object from button click. Defaults to None.
        
        Returns:
            None
        
        Side Effects:
            - Clears and repopulates self.risk_col with learner containers
            - Updates the page display
        """
        self.risk_col.controls.clear()
        data = fetch(f"/students-at-risk/{self.onto_field.value}", ALERTS_API)
        
        if not data:
            self.risk_col.controls.append(ft.Text("Aucun résultat.", color="#BDBDBD"))
        else:
            for d in data:
                progression = d.get('progression', 0)
                color_progression = "#4CAF50" if progression > 0.7 else ("#FF9800" if progression > 0.4 else "#FF5252")
                
                learner_info = ft.Column([
                    ft.Row([
                        ft.Text(f"Apprenant #{d['id_apprenant']}", size=14, weight=ft.FontWeight.W_500, expand=True),
                        ft.Text(f"⚠️ {d.get('aavs_bloques', 0)} bloqué(s)", color="#FF5252", weight=ft.FontWeight.W_500),
                    ]),
                    ft.Divider(height=1),
                    row("Nom", d.get('nom', 'N/A')),
                    row("Progression globale", f"{round(progression * 100, 1)}%", color_progression),
                    row("AAVs bloqués", str(d.get('aavs_bloques', 0)), "#FF5252" if d.get('aavs_bloques', 0) > 0 else "#FFFFFF"),
                ], spacing=4)
                
                self.risk_col.controls.append(
                    ft.Container(
                        content=learner_info,
                        bgcolor="#2a2a3e",
                        border_radius=10,
                        padding=12,
                        margin=ft.margin.only(bottom=8),
                    )
                )
        
        if hasattr(self, '_page'):
            self._page.update()
    
    def make_clickable_aav_row(self, aav_data, color, extra_info=""):
        """
        Create a clickable container row for an AAV item.
        
        Generates an interactive row that displays AAV name and success rate,
        with click handling to navigate to the AAV details page.
        
        Args:
            aav_data (dict): Dictionary containing AAV information with keys:
                - 'nom' (str): AAV name
                - 'id_aav' (int): AAV identifier
                - 'taux_succes' (float, optional): Success rate as decimal (0.0-1.0)
            color (str): Flet color constant for the success rate text (e.g., "#FF5252")
            extra_info (str, optional): Additional info to display on the right
        
        Returns:
            ft.Container: Interactive container with row layout and click handler
        """
        def on_click(e):
            self.show_details(aav_data['id_aav'])
        
        return ft.Container(
            content=ft.Row([
                ft.Text(aav_data["nom"], expand=True, color="#E0E0E0"),
                ft.Text(extra_info if extra_info else f"{int(aav_data.get('taux_succes', 0)*100)}%", color=color, weight=ft.FontWeight.W_500),
            ]),
            on_click=on_click,
            ink=True,
        )
    
    def build(self, page):
        """
        Build and return the complete alerts dashboard UI.
        
        Constructs the alerts dashboard displaying:
        - Metrics cards for difficult, unused, and fragile AAV counts
        - Sections for each alert type with clickable AAV rows
        - Search field for students at risk by ontology ID
        
        Args:
            page (ft.Page): The Flet page object for UI updates
        
        Returns:
            ft.Column: Complete alerts page UI column containing all dashboard elements
        
        Side Effects:
            - Fetches data from three API endpoints: difficult-aavs, unused-aavs, fragile-aavs
            - Stores page reference for later updates via self._page
        """
        self._page = page
        
        difficult = fetch("/difficult-aavs", ALERTS_API)
        unused    = fetch("/unused-aavs", ALERTS_API)
        fragile   = fetch("/fragile-aavs", ALERTS_API)
        
        self.page_content = ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("Alert Dashboard", size=24, weight=ft.FontWeight.W_500),
                    ft.Text("AAV monitoring", color="#BDBDBD", size=13),
                ], expand=True),
                ft.ElevatedButton(
                    "Back to About",
                    on_click=self.show_about,
                    icon=ft.Icons.ARROW_BACK,
                ),
            ], spacing=10),
            ft.Divider(height=20, color="transparent"),
            ft.Row([
                ft.Container(ft.Column([ft.Text(str(len(difficult)), size=28, weight=ft.FontWeight.W_500), ft.Text("Difficult", color="#BDBDBD", size=12)]), bgcolor="#B71C1C",    border_radius=8, padding=16, expand=True),
                ft.Container(ft.Column([ft.Text(str(len(unused)),    size=28, weight=ft.FontWeight.W_500), ft.Text("Unused",    color="#BDBDBD", size=12)]), bgcolor="#E65100", border_radius=8, padding=16, expand=True),
                ft.Container(ft.Column([ft.Text(str(len(fragile)),   size=28, weight=ft.FontWeight.W_500), ft.Text("Fragile",   color="#BDBDBD", size=12)]), bgcolor="#1565C0",   border_radius=8, padding=16, expand=True),
            ], spacing=10),
            ft.Divider(height=20, color="transparent"),
            section("Difficult AAVs (click to view details)", [
                self.make_clickable_aav_row(d, "#FF5252") for d in difficult
            ]),
            ft.Divider(height=15, color="transparent"),
            section("Unused AAVs (click to view details)", [
                self.make_clickable_aav_row(d, "#FF9800", f"{d.get('nombre_utilisations', 0)} uses") for d in unused
            ]),
            ft.Divider(height=15, color="transparent"),
            section("Fragile AAVs (click to view details)", [
                self.make_clickable_aav_row(d, "#42A5F5", f"σ={round(d.get('variance', 0), 1)}") for d in fragile
            ]),
            ft.Divider(height=15, color="transparent"),
            ft.Row([self.onto_field, ft.ElevatedButton("Search", on_click=self.load_risk)], vertical_alignment=ft.CrossAxisAlignment.END, spacing=10),
            self.risk_col,
        ], scroll=ft.ScrollMode.AUTO, spacing=0)
        
        return self.page_content
