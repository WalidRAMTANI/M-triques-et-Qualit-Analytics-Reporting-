from pydantic import BaseModel, Field
from typing import Literal, Union, Optional
from datetime import date, datetime


# ============================================================
# Schemas for Alert Endpoints
# ============================================================

class AAVDifficile(BaseModel):
    """Représente un AAV dont le taux de succès est trop bas."""
    id_aav: int = Field(..., description="Identifiant unique de l'AAV")
    nom: str = Field(..., description="Nom de l'AAV")
    taux_succes: float = Field(..., ge=0.0, le=1.0, description="Taux de succès moyen entre 0 et 1")
    nb_tentatives: int = Field(..., ge=0, description="Nombre total de tentatives")
    suggestion: str = Field(..., description="Suggestion pédagogique pour améliorer l'AAV")

class AAVInutilise(BaseModel):
    """Modèle complet d'un AAV (réponse API)."""
    id_aav: int
    nom: str

class AAVFragile(BaseModel):
    """Modèle complet d'un AAV (réponse API)."""
    id_aav: int
    nom: str
    ecart_type_scores: float
    nb_tentatives: int
    score_min: float
    score_max: float
    suggestion: str

class ApprenantRisque(BaseModel):
    """Modèle complet d'un apprenant (réponse API)."""
    id_apprenant: int
    nom: str
    progression: float
    aavs_bloques: int


# ============================================================
# Schemas for Report Endpoints
# ============================================================

class RapportResponse(BaseModel):
    """Modèle complet d'un rapport (réponse API)."""
    type_rapport: str
    id_cible: Union[str, int]
    periode_debut: datetime
    periode_fin: datetime
    format: str
    date_generation: datetime
    contenu: Union[dict, str]
    format_fichier: str


class RapportRequest(BaseModel):
    """Corps de la requête pour générer un rapport."""
    type: Literal["discipline", "aav", "student"]
    id_cible: Union[str, int]
    date_debut: date
    date_fin: date
    format: Literal["json", "csv", "pdf"]

class RapportGlobalResponse(BaseModel):
    """Modèle complet d'un rapport global (réponse API)."""
    date_generation: str
    nb_aavs_total: int
    nb_aavs_utilisables: int
    nb_alertes: dict
    alertes: dict
    aavs: list

# ============================================
# Schemas for Comparison Endpoints
# ============================================

class AAVComparaison(BaseModel):
    id_aav: int
    nom: str
    taux_succes: float
    couverture: float
    utilisabilite: bool
    nb_tentatives: int
    nb_apprenants: int

class ApprenantComparaison(BaseModel):
    id_apprenant: int
    nom: str
    nb_tentatives: int
    progression: float
    aavs_bloques: int       

class TeacherDashboard(BaseModel):
    moyenne: float
    nb_aav: int
    nb_apprenants: int

class DisciplineDashboard(BaseModel):
    moyenne : float
    moyenne_covering : float
    nb : int

class OntologyCoverage(BaseModel):
    """Schéma pour la couverture d'une ontologie."""
    nb_aav: int
    moyenne_covering: float