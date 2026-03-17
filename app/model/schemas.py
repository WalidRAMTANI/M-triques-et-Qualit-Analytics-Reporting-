from pydantic import BaseModel, Field
from typing import Literal, Union, Optional
from datetime import date, datetime


# ============================================================
# Schemas for Alert Endpoints
# ============================================================

class AAVDifficile(BaseModel):
    """Represents an AAV with an abnormally low success rate."""
    id_aav: int = Field(..., description="Unique ID of the AAV")
    nom: str = Field(..., description="Name of the AAV")
    taux_succes: float = Field(..., ge=0.0, le=1.0, description="Average success rate between 0 and 1")
    nb_tentatives: int = Field(..., ge=0, description="Total number of attempts")
    suggestion: str = Field(..., description="Pedagogical suggestion to improve the AAV")

class AAVInutilise(BaseModel):
    """Represents an unused AAV."""
    id_aav: int
    nom: str

class AAVFragile(BaseModel):
    """Represents a fragile AAV with highly variable scores."""
    id_aav: int
    nom: str
    ecart_type_scores: float
    nb_tentatives: int
    score_min: float
    score_max: float
    suggestion: str

class ApprenantRisque(BaseModel):
    """Represents an at-risk learner."""
    id_apprenant: int
    nom: str
    progression: float
    aavs_bloques: int


# ============================================================
# Schemas for Report Endpoints
# ============================================================

class RapportResponse(BaseModel):
    """Complete model for a report (API response)."""
    type_rapport: str
    id_cible: Union[str, int]
    periode_debut: datetime
    periode_fin: datetime
    format: str
    date_generation: datetime
    contenu: Union[dict, str]
    format_fichier: str


class RapportRequest(BaseModel):
    """Request body to generate a report."""
    type: Literal["discipline", "aav", "student"]
    id_cible: Union[str, int]
    debut: Optional[datetime] = None
    fin: Optional[datetime] = None
    format: Literal["json", "csv", "pdf"]

class RapportGlobalResponse(BaseModel):
    """Complete model for a global report (API response)."""
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
    disciplines: list[str]

class DisciplineDashboard(BaseModel):
    moyenne : float
    moyenne_covering : float
    nb : int

class OntologyCoverage(BaseModel):
    """Schema for the coverage of an ontology."""
    nb_aav: int
    moyenne_covering: float