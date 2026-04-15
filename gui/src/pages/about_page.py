import sys
import flet as ft
from pathlib import Path

# Configuration du chemin racine pour les imports internes
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

class AboutPage:
    """
    Page de presentation institutionnelle du projet AAV Dashboard.
    Regroupe les informations techniques, les objectifs pedagogiques et la documentation.
    """
    
    def __init__(self, content_area, show_alerts_callback):
        """Initialise la page avec les callbacks de navigation peripherique."""
        self.content_area = content_area
        self.show_alerts = show_alerts_callback
        self.page_content = None
    
    def build(self, page):
        """Genere l'interface descriptive de la solution logicielle."""
        self.page_content = ft.Column(
            [
                ft.Row([
                    ft.Column([
                        ft.Text("Tableau de Bord AAV", size=32, weight=ft.FontWeight.W_700),
                        ft.Text("Systeme de Suivi des Activites d'Apprentissage - v1.3", color="#BDBDBD", size=14),
                    ], expand=True),
                ], expand=True),
                ft.Divider(),
                
                self._build_section(
                    "Architecture du Projet",
                    "Le tableau de bord AAV est un systeme d'analyse multicritere permettant le suivi "
                    "des acquis d'apprentissage transversaux. Il centralise les donnees de progression "
                    "en temps reel pour identifier les cohortes d'apprenants a risque et optimiser "
                    "les ressources pedagogiques proposees."
                ),
                self._build_section(
                    "Objectifs Institutionnels",
                    [
                        "- Monitorer les activites critiques (difficiles, sous-utilisees, fragiles)",
                        "- Identifier les ruptures de parcours academique",
                        "- Analyser les taux de reussite et l'engagement des apprenants",
                        "- Fournir des indicateurs decisionnels pour l'amelioration continue",
                    ],
                ),
                self._build_section(
                    "Fonctionnalites Cles",
                    [
                        "- Dashboard d'alertes : Visualisation instantanee de l'etat des AAV",
                        "- Detection de Risques : Analyse comportementale et predictive",
                        "- Referentiel de Competences : Consultation detaillee des metadonnees",
                        "- Export de Rapports : Generation automatique de diagnostics PDF",
                    ],
                ),
                self._build_section(
                    "Environnement Technique",
                    [
                        "Interface Utilisateur : Flet (Python UI Framework)",
                        "Serveur d'API : FastAPI (Python High-Performance Web Framework)",
                        "Persistance des donnees : SQLAlchemy ORM / SQLite",
                        "Protocole de communication : Connecteur RESTful (Httpx)",
                    ],
                ),
                self._build_section(
                    "Architecture Logicielle",
                    [
                        "main.py : Orchestrateur de navigation et gestion de session",
                        "alert_page.py : Hub de monitoring de la qualite pedagogique",
                        "aav_detail_page.py : Analyse unitaire des referentiels",
                        "reports_page.py : Moteur de generation documentaire scientifique",
                    ],
                ),
                ft.Divider(),
                ft.Container(
                    content=ft.Column([
                        ft.Text("© 2026 Equipe de Recherche - Tous Droits Reserves", size=11, color="#BDBDBD", text_align=ft.TextAlign.CENTER),
                        ft.Text("Propulse par Flet et FastAPI", size=10, color="#424242", text_align=ft.TextAlign.CENTER),
                    ], spacing=4),
                    alignment=ft.Alignment(0, 0), padding=20
                ),
            ],
            scroll=ft.ScrollMode.AUTO, spacing=16
        )
        return self.page_content
    
    def _build_section(self, title, content):
        """Construit un bloc informatif standardise pour la mise en page."""
        content_controls = [
            ft.Text(title, size=14, weight=ft.FontWeight.W_600, color="#CE93D8"),
            ft.Divider(height=1),
        ]
        
        if isinstance(content, list):
            for item in content:
                content_controls.append(ft.Text(item, size=11, color="#E0E0E0", selectable=True))
        else:
            content_controls.append(ft.Text(content, size=11, color="#E0E0E0", selectable=True))
        
        return ft.Container(
            content=ft.Column(content_controls, spacing=8),
            bgcolor="#2a2a3e", border_radius=10, padding=16
        )
