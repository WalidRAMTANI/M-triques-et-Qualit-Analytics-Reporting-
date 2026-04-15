import sys
import flet as ft
from pathlib import Path

# Configuration du chemin racine pour les imports internes
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

class Sidebar:
    """
    Composant de navigation lateral (Sidebar).
    Assure l'aiguillage entre les differents modules analytiques et CRUD.
    """
    
    def __init__(
        self,
        show_alerts_cb,
        show_about_cb,
        show_aav_detail_cb=None,
        show_dashboard_cb=None,
        show_metrics_cb=None,
        show_sessions_cb=None,
        show_aavs_cb=None,
        show_activitePedagogique_cb=None,
        show_attempts_cb=None,
        show_comparaison_cb=None,
        show_exerciseEngine_cb=None,
        show_learners_cb=None,
        show_navigation_cb=None,
        show_ontologies_cb=None,
        show_promptFabricationAAV_cb=None,
        show_remediation_cb=None,
        show_reports_cb=None,
        show_statuts_cb=None,
        show_types_cb=None,
        show_dashboard_page_cb=None,
        show_sessions_page_cb=None,
        show_admin_cb=None,
        is_professor=False
    ):
        """Initialise la sidebar avec l'ensemble des callbacks de navigation."""
        self.show_alerts = show_alerts_cb
        self.show_about = show_about_cb
        self.show_aav_detail = show_aav_detail_cb
        self.show_dashboard = show_dashboard_cb
        self.show_metrics = show_metrics_cb
        self.show_sessions = show_sessions_cb
        self.show_aavs = show_aavs_cb
        self.show_activitePedagogique = show_activitePedagogique_cb
        self.show_attempts = show_attempts_cb
        self.show_comparaison = show_comparaison_cb
        self.show_exerciseEngine = show_exerciseEngine_cb
        self.show_learners = show_learners_cb
        self.show_navigation = show_navigation_cb
        self.show_ontologies = show_ontologies_cb
        self.show_promptFabricationAAV = show_promptFabricationAAV_cb
        self.show_remediation = show_remediation_cb
        self.show_reports = show_reports_cb
        self.show_statuts = show_statuts_cb
        self.show_types = show_types_cb
        self.show_dashboard_page = show_dashboard_page_cb
        self.show_sessions_page = show_sessions_page_cb
        self.show_admin = show_admin_cb
        self.is_professor = is_professor
        self.role_indicator = ft.Container()
        self.sidebar_content = None
    
    def update_role(self, is_prof):
        """Met a jour dynamiquement l'interface selon le changement de privileges."""
        self.is_professor = is_prof
        if self.role_indicator:
            self.role_indicator.content.value = "MODE PROFESSEUR" if is_prof else "MODE APPRENANT"
            self.role_indicator.bgcolor = "#2E7D32" if is_prof else "#1565C0"
            self.role_indicator.update()

    def build(self):
        """
        Build and return the sidebar UI component.
        """
        self.role_indicator = ft.Container(
            content=ft.Text("MODE PROFESSEUR" if self.is_professor else "MODE APPRENANT", size=11, weight="bold", color="white"),
            bgcolor="#2E7D32" if self.is_professor else "#1565C0",
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            border_radius=15,
            margin=ft.margin.only(bottom=10)
        )

        self.sidebar_content = ft.Container(
            content=ft.Column(
                [
                    # Header Section
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.Icons.DASHBOARD, size=40, color="#9C27B0"),
                                ft.Text(
                                    "AAV Analytics",
                                    size=18,
                                    weight=ft.FontWeight.W_700,
                                    color="#FFFFFF",
                                ),
                                self.role_indicator,
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        bgcolor="#4A148C",
                        border_radius=10,
                        padding=16,
                        margin=ft.margin.only(bottom=20),
                    ),
                    
                    # Administration Button
                    ft.ElevatedButton(
                        content=ft.Row([ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=20), ft.Text("Authentification Admin", expand=True)], spacing=10),
                        on_click=self.show_admin,
                        style=ft.ButtonStyle(color="#FFFFFF", bgcolor={ft.ControlState.DEFAULT: "#FBC02D" if not self.is_professor else "#7B1FA2"}),
                        width=200,
                    ),

                    ft.Divider(height=10, color="transparent"),

                    # Navigation Buttons Section (Top)
                    ft.Text(
                        "Navigation",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color="#E0E0E0",
                    ),
                    
                    ft.ElevatedButton(
                        content=ft.Row([ft.Icon(ft.Icons.WARNING, size=20), ft.Text("Alertes Critiques", expand=True)], spacing=10),
                        on_click=self.show_alerts,
                        style=ft.ButtonStyle(color="#FFFFFF", bgcolor={ft.ControlState.DEFAULT: "#B71C1C"}),
                        width=200,
                    ),
                    
                    ft.ElevatedButton(
                        content=ft.Row([ft.Icon(ft.Icons.ANALYTICS, size=20), ft.Text("AAV Détail", expand=True)], spacing=10),
                        on_click=self.show_aav_detail,
                        style=ft.ButtonStyle(color="#FFFFFF", bgcolor={ft.ControlState.DEFAULT: "#4A148C"}),
                        width=200,
                    ),
                    
                    ft.ElevatedButton(
                        content=ft.Row([ft.Icon(ft.Icons.DASHBOARD_CUSTOMIZE, size=20), ft.Text("Graphe Dashboard", expand=True)], spacing=10),
                        on_click=self.show_dashboard,
                        style=ft.ButtonStyle(color="#FFFFFF", bgcolor={ft.ControlState.DEFAULT: "#1565C0"}),
                        width=200,
                    ),
                    
                    ft.ElevatedButton(
                        content=ft.Row([ft.Icon(ft.Icons.BAR_CHART, size=20), ft.Text("Métriques Graph", expand=True)], spacing=10),
                        on_click=self.show_metrics,
                        style=ft.ButtonStyle(color="#FFFFFF", bgcolor={ft.ControlState.DEFAULT: "#00695C"}),
                        width=200,
                    ),
                    
                    ft.ElevatedButton(
                        content=ft.Row([ft.Icon(ft.Icons.TIMER, size=20), ft.Text("Graphe Sessions", expand=True)], spacing=10),
                        on_click=self.show_sessions,
                        style=ft.ButtonStyle(color="#FFFFFF", bgcolor={ft.ControlState.DEFAULT: "#E65100"}),
                        width=200,
                    ),
                    
                    ft.ElevatedButton(
                        content=ft.Row([ft.Icon(ft.Icons.INFO, size=20), ft.Text("Support et Infos", expand=True)], spacing=10),
                        on_click=self.show_about,
                        style=ft.ButtonStyle(color="#FFFFFF", bgcolor={ft.ControlState.DEFAULT: "#37474F"}),
                        width=200,
                    ),
                    
                    ft.Divider(height=20),
                    
                    # Fonctions – toutes les pages modules
                    ft.Text("Referentiels et Modules", size=12, weight=ft.FontWeight.W_600, color="#E0E0E0"),

                    ft.TextButton("Synthese des Alertes", icon=ft.Icons.WARNING, on_click=self.show_alerts),
                    ft.TextButton("Fiche Technique AAV", icon=ft.Icons.ANALYTICS, on_click=self.show_aav_detail),
                    ft.TextButton("Analyse des Metriques", icon=ft.Icons.BAR_CHART, on_click=self.show_metrics),
                    ft.TextButton("Referentiel des AAV", icon=ft.Icons.SCHOOL, on_click=self.show_aavs),
                    ft.TextButton("Pilotage Dashboard", icon=ft.Icons.STORAGE, on_click=self.show_dashboard_page, visible=self.is_professor),
                    ft.TextButton("Pilotage Sessions", icon=ft.Icons.ALARM, on_click=self.show_sessions_page, visible=self.is_professor),
                    ft.TextButton("Referentiel Apprenants", icon=ft.Icons.PEOPLE, on_click=self.show_learners),
                    ft.TextButton("Activites Academiques", icon=ft.Icons.FITNESS_CENTER, on_click=self.show_activitePedagogique),
                    ft.TextButton("Historique Tentatives", icon=ft.Icons.ASSIGNMENT, on_click=self.show_attempts),
                    ft.TextButton("Module Comparaison", icon=ft.Icons.COMPARE_ARROWS, on_click=self.show_comparaison),
                    ft.TextButton("Moteur d'Exercices", icon=ft.Icons.SETTINGS, on_click=self.show_exerciseEngine),
                    ft.TextButton("Parcours Navigation", icon=ft.Icons.EXPLORE, on_click=self.show_navigation),
                    ft.TextButton("Exploration Ontologies", icon=ft.Icons.ACCOUNT_TREE, on_click=self.show_ontologies),
                    ft.TextButton("Referentiel Prompts", icon=ft.Icons.TEXT_SNIPPET, on_click=self.show_promptFabricationAAV, visible=self.is_professor),
                    ft.TextButton("Solution Remediation", icon=ft.Icons.MEDICAL_SERVICES, on_click=self.show_remediation),
                    ft.TextButton("Edition des Rapports", icon=ft.Icons.PICTURE_AS_PDF, on_click=self.show_reports),
                    ft.TextButton("Statuts Acquisition", icon=ft.Icons.BOOKMARK, on_click=self.show_statuts),
                    ft.TextButton("Dictionnaires Types", icon=ft.Icons.CATEGORY, on_click=self.show_types),
                    
                    ft.Divider(height=20),
                    
                    # Project Info Section
                    ft.Text(
                        "À propos du projet",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color="#E0E0E0",
                    ),
                    
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Plateforme de Monitoring AAV",
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                    color="#FFFFFF",
                                ),
                                ft.Text(
                                    "Systeme analytique pour la supervision des "
                                    "Acquis d'Apprentissage (AAV). "
                                    "Analyse des blocages, des ressources sous-utilisees "
                                    "et identification des cohortes a risque.",
                                    size=11,
                                    color="#E0E0E0",
                                    selectable=True,
                                ),
                            ],
                            spacing=8,
                        ),
                        bgcolor="#2a2a3e",
                        border_radius=8,
                        padding=12,
                    ),
                    
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.START,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=16,
            expand=True
        )
        
        return self.sidebar_content
