"""
Alert Dashboard page for AAV monitoring.

Displays alerts for difficult, unused, and fragile AAVs,
and allows searching for students at risk.
"""

import flet as ft
from utils import fetch, row, section, ALERTS_API


class AlertsPage:
    """Alert Dashboard page showing difficult, unused, and fragile AAVs."""
    
    def __init__(self, content_area, show_details_callback):
        self.content_area = content_area
        self.show_details = show_details_callback
        self.onto_field = ft.TextField(label="Ontologie ID", width=200, dense=True)
        self.risk_col = ft.Column()
        self.page_content = None
    
    def load_risk(self, e=None):
        """Load students at risk for given ontology ID."""
        self.risk_col.controls.clear()
        data = fetch(f"/students-at-risk/{self.onto_field.value}", ALERTS_API)
        
        if not data:
            self.risk_col.controls.append(ft.Text("Aucun résultat.", color=ft.Colors.WHITE38))
        else:
            for d in data:
                progression = d.get('progression', 0)
                color_progression = ft.Colors.GREEN_300 if progression > 0.7 else (ft.Colors.ORANGE_300 if progression > 0.4 else ft.Colors.RED_300)
                
                learner_info = ft.Column([
                    ft.Row([
                        ft.Text(f"Apprenant #{d['id_apprenant']}", size=14, weight=ft.FontWeight.W_500, expand=True),
                        ft.Text(f"⚠️ {d.get('aavs_bloques', 0)} bloqué(s)", color=ft.Colors.RED_300, weight=ft.FontWeight.W_500),
                    ]),
                    ft.Divider(height=1),
                    row("Nom", d.get('nom', 'N/A')),
                    row("Progression globale", f"{round(progression * 100, 1)}%", color_progression),
                    row("AAVs bloqués", str(d.get('aavs_bloques', 0)), ft.Colors.RED_300 if d.get('aavs_bloques', 0) > 0 else ft.Colors.WHITE),
                ], spacing=4)
                
                self.risk_col.controls.append(
                    ft.Container(
                        content=learner_info,
                        bgcolor=ft.Colors.WHITE10,
                        border_radius=10,
                        padding=12,
                        margin=ft.margin.only(bottom=8),
                    )
                )
        
        if hasattr(self, '_page'):
            self._page.update()
    
    def make_clickable_aav_row(self, aav_data, color):
        """Create a clickable row for an AAV."""
        def on_click(e):
            self.show_details(aav_data['id_aav'])
        
        return ft.Container(
            content=ft.Row([
                ft.Text(aav_data["nom"], expand=True, color=ft.Colors.WHITE70),
                ft.Text(f"{int(aav_data.get('taux_succes', 0)*100)}%", color=color, weight=ft.FontWeight.W_500),
            ]),
            on_click=on_click,
            ink=True,
        )
    
    def build(self, page):
        """Build the alerts page."""
        self._page = page
        
        difficult = fetch("/difficult-aavs", ALERTS_API)
        unused    = fetch("/unused-aavs", ALERTS_API)
        fragile   = fetch("/fragile-aavs", ALERTS_API)
        
        self.page_content = ft.Column([
            ft.Text("Alert Dashboard", size=24, weight=ft.FontWeight.W_500),
            ft.Text("AAV monitoring", color=ft.Colors.WHITE38, size=13),
            ft.Row([
                ft.Container(ft.Column([ft.Text(str(len(difficult)), size=28, weight=ft.FontWeight.W_500), ft.Text("Difficult", color=ft.Colors.WHITE38, size=12)]), bgcolor=ft.Colors.RED_900,    border_radius=8, padding=16, expand=True),
                ft.Container(ft.Column([ft.Text(str(len(unused)),    size=28, weight=ft.FontWeight.W_500), ft.Text("Unused",    color=ft.Colors.WHITE38, size=12)]), bgcolor=ft.Colors.ORANGE_900, border_radius=8, padding=16, expand=True),
                ft.Container(ft.Column([ft.Text(str(len(fragile)),   size=28, weight=ft.FontWeight.W_500), ft.Text("Fragile",   color=ft.Colors.WHITE38, size=12)]), bgcolor=ft.Colors.BLUE_900,   border_radius=8, padding=16, expand=True),
            ], spacing=10),
            section("Difficult AAVs (click to view details)", [
                self.make_clickable_aav_row(d, ft.Colors.RED_300) for d in difficult
            ]),
            section("Unused AAVs", [
                row(d["nom"], f"{d.get('nombre_utilisations', 0)} uses", ft.Colors.ORANGE_300) for d in unused
            ]),
            section("Fragile AAVs", [
                row(d["nom"], f"σ={round(d.get('variance', 0), 1)}", ft.Colors.BLUE_300) for d in fragile
            ]),
            ft.Row([self.onto_field, ft.ElevatedButton("Search", on_click=self.load_risk)], vertical_alignment=ft.CrossAxisAlignment.END),
            self.risk_col,
        ], scroll=ft.ScrollMode.AUTO)
        
        return self.page_content
