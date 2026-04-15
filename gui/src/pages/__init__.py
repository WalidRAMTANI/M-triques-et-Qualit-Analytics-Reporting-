"""
Module centralisant l'ensemble des vues et composants graphiques de l'application AAV Dashboard.
Assure l'exportation unifiee pour simplifier les structures d'import internes.
"""

from .about_page import AboutPage
from .aav_detail_page import DetailsPage
from .aavs_page import AavsPage
from .activitePedagogique_page import ActivitepedagogiquePage
from .admin_page import AdminPage
from .alert_page import AlertsPage
from .attempts_page import AttemptsPage
from .comparaison_page import ComparaisonPage
from .dashboard_page import DashboardPage
from .exerciseEngine_page import ExerciseenginePage
from .learners_page import LearnersPage
from .navigation_page import NavigationPage
from .ontologies_page import OntologiesPage
from .promptFabricationAAV_page import PromptfabricationaavPage
from .remediation_page import RemediationPage
from .reports_page import ReportsPage
from .sessions_page import SessionsPage
from .sidebar import Sidebar
from .statuts_page import StatutsPage
from .types_page import TypesPage

__all__ = [
    "AboutPage",
    "DetailsPage",
    "AavsPage",
    "ActivitepedagogiquePage",
    "AdminPage",
    "AlertsPage",
    "AttemptsPage",
    "ComparaisonPage",
    "DashboardPage",
    "ExerciseenginePage",
    "LearnersPage",
    "NavigationPage",
    "OntologiesPage",
    "PromptfabricationaavPage",
    "RemediationPage",
    "ReportsPage",
    "SessionsPage",
    "Sidebar",
    "StatutsPage",
    "TypesPage",
]
