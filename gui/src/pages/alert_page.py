import sys
import flet as ft
from pathlib import Path

# Configuration du chemin racine pour les imports internes
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import des utilitaires de communication API
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import fetch, row, section, ALERTS_API

class AlertsPage:
    """
    Page de monitoring et de gestion des alertes pedagogiques.
    Permet d'identifier les AAV critiques (difficiles, orphelins, fragiles)
    et de detecter les apprenants en situation de blocage.
    """
    
    def __init__(self, content_area, show_details_callback, show_about_callback):
        """Initialise la page avec les callbacks de navigation et les composants de recherche."""
        self.content_area = content_area
        self.show_details = show_details_callback
        self.show_about = show_about_callback
        self.onto_field = ft.TextField(label="ID de l'Ontologie", width=200, dense=True)
        self.risk_col = ft.Column()
        self.page_content = None
    
    def load_risk(self, e=None):
        """
        Recupere et affiche les apprenants a risque pour une ontologie donnee.
        Analyse la progression et le nombre d'AAV bloques pour chaque profil.
        """
        self.risk_col.controls.clear()
        try:
            data = fetch(f"/students-at-risk/{self.onto_field.value}", ALERTS_API)
            if not data:
                self.risk_col.controls.append(ft.Text("Aucun apprenant en difficulte detecte.", color="#BDBDBD"))
            else:
                for d in data:
                    progression = d.get('progression', 0)
                    color_progression = "#4CAF50" if progression > 0.7 else ("#FF9800" if progression > 0.4 else "#FF5252")
                    
                    learner_info = ft.Column([
                        ft.Row([
                            ft.Text(f"Apprenant #{d['id_apprenant']}", size=14, weight=ft.FontWeight.W_500, expand=True),
                            ft.Text(f"Blocages : {d.get('aavs_bloques', 0)}", color="#FF5252", weight=ft.FontWeight.W_500),
                        ]),
                        ft.Divider(height=1),
                        row("Nom de l'apprenant", d.get('nom', 'Anonyme')),
                        row("Progression validee", f"{round(progression * 100, 1)}%", color_progression),
                        row("AAV en echec", str(d.get('aavs_bloques', 0)), "#FF5252" if d.get('aavs_bloques', 0) > 0 else "#FFFFFF"),
                    ], spacing=4)
                    
                    self.risk_col.controls.append(
                        ft.Container(
                            content=learner_info, bgcolor="#2a2a3e", border_radius=10,
                            padding=12, margin=ft.margin.only(bottom=8)
                        )
                    )
        except:
            self.risk_col.controls.append(ft.Text("Erreur lors de l'analyse des risques.", color="#FF5252"))
        
        if hasattr(self, '_page'):
            self._page.update()
    
    def make_clickable_aav_row(self, aav_data, color, extra_info=""):
        """Genere une ligne interactive pour consulter les details d'un referentiel AAV."""
        def on_click(e):
            self.show_details(aav_data['id_aav'])
        
        return ft.Container(
            content=ft.Row([
                ft.Text(aav_data["nom"], expand=True, color="#E0E0E0"),
                ft.Text(extra_info if extra_info else f"{int(aav_data.get('taux_succes', 0)*100)}%", color=color, weight=ft.FontWeight.W_500),
            ]),
            on_click=on_click, ink=True
        )
    
    def build(self, page):
        """Construit le tableau de bord des alertes avec les indicateurs de performance."""
        self._page = page
        difficult = fetch("/difficult-aavs", ALERTS_API)
        unused = fetch("/unused-aavs", ALERTS_API)
        fragile = fetch("/fragile-aavs", ALERTS_API)
        
        self.page_content = ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("Tableau de Bord des Alertes", size=24, weight=ft.FontWeight.W_500),
                    ft.Text("Supervision de la qualite pedagogique", color="#BDBDBD", size=13),
                ], expand=True),
                ft.ElevatedButton("Retour A propos", on_click=self.show_about, icon=ft.Icons.ARROW_BACK),
            ], spacing=10),
            ft.Divider(height=20, color="transparent"),
            ft.Row([
                ft.Container(ft.Column([ft.Text(str(len(difficult)), size=28, weight=ft.FontWeight.W_500), ft.Text("Difficiles", color="#BDBDBD", size=12)]), bgcolor="#B71C1C", border_radius=8, padding=16, expand=True),
                ft.Container(ft.Column([ft.Text(str(len(unused)), size=28, weight=ft.FontWeight.W_500), ft.Text("Orphelins", color="#BDBDBD", size=12)]), bgcolor="#E65100", border_radius=8, padding=16, expand=True),
                ft.Container(ft.Column([ft.Text(str(len(fragile)), size=28, weight=ft.FontWeight.W_500), ft.Text("Fragiles", color="#BDBDBD", size=12)]), bgcolor="#1565C0", border_radius=8, padding=16, expand=True),
            ], spacing=10),
            ft.Divider(height=20, color="transparent"),
            section("AAV Critiques (cliquer pour le detail)", [self.make_clickable_aav_row(d, "#FF5252") for d in difficult]),
            ft.Divider(height=15, color="transparent"),
            section("AAV Inutilises", [self.make_clickable_aav_row(d, "#FF9800", f"{d.get('nombre_utilisations', 0)} usages") for d in unused]),
            ft.Divider(height=15, color="transparent"),
            section("AAV Instables (High Variance)", [self.make_clickable_aav_row(d, "#42A5F5", f"var={round(d.get('variance', 0), 1)}") for d in fragile]),
            ft.Divider(height=15, color="transparent"),
            ft.Row([self.onto_field, ft.ElevatedButton("Analyser Risques", on_click=self.load_risk)], vertical_alignment=ft.CrossAxisAlignment.END, spacing=10),
            self.risk_col,
        ], scroll=ft.ScrollMode.AUTO, spacing=0)
        
        return self.page_content
