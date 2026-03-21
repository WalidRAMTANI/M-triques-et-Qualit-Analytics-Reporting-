# app/model/schemas.py
"""
Pydantic schemas for validation of API requests/responses.

This file contains all Pydantic models used for:
- Validating incoming data (POST/PUT requests)
- Serializing outgoing data (JSON responses)
- Documenting FastAPI endpoints

All models inherit from BaseModel (Pydantic v2).
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Union
from enum import Enum
from datetime import datetime


# ============================================================
# ENUMERATIONS
# ============================================================

class TypeEvaluationAAV(str, Enum):
    """Possible evaluation types for an AAV."""
    HUMAINE = "Humaine"
    CALCUL = "Calcul Automatisé"
    CHUTE = "Compréhension par Chute"
    INVENTION = "Validation par Invention"
    CRITIQUE = "Exercice de Critique"
    EVALUATION_PAIRS = "Évaluation par les Pairs"
    EVALUATION_AGREGEE = "Agrégation (Composite)"


class TypeAAV(str, Enum):
    """Possible AAV types."""
    ATOMIQUE = "Atomique"
    COMPOSITE = "Composite (Chapitre)"


class NiveauDifficulte(str, Enum):
    """Difficulty levels for exercises."""
    DEBUTANT = "debutant"
    INTERMEDIAIRE = "intermediaire"
    AVANCE = "avance"


class TypeActivite(str, Enum):
    """Activity type for exercises."""
    PILOTEE = "pilotee"
    PROF = "prof_definie"
    REVISION = "revision"


# ============================================================
# BASE MODELS (Common to all groups)
# ============================================================

class RegleProgression(BaseModel):
    """
    Rules determining how a learner progresses on an AAV.

    Example:
        - seuil_succes: 0.7 (70% to succeed)
        - nombre_succes_consecutifs: 3 (3 consecutive successes = mastery)
    """
    model_config = ConfigDict(from_attributes=True)

    seuil_succes: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum score to consider an attempt as successful",
    )
    maitrise_requise: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Mastery level to achieve for AAV validation",
    )
    nombre_succes_consecutifs: int = Field(
        default=1, ge=1, description="Number of consecutive successes required"
    )
    nombre_jugements_pairs_requis: int = Field(
        default=3,
        ge=1,
        description="For peer evaluation: required judgments",
    )
    tolerance_jugement: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Tolerance margin for peer evaluations",
    )


class AAVBase(BaseModel):
    """Base fields for an AAV (creation and update)."""
    model_config = ConfigDict(from_attributes=True)

    nom: str = Field(
        ..., min_length=3, max_length=200, description="Technical name of the AAV"
    )
    libelle_integration: str = Field(
        ...,
        min_length=5,
        description="Grammatical form for insertion in a sentence",
    )
    discipline: str = Field(
        ..., min_length=2, description="Discipline (ex: Mathematics)"
    )
    enseignement: str = Field(..., description="Specific teaching (ex: Algebra)")
    type_aav: TypeAAV
    description_markdown: str = Field(
        ..., min_length=10, description="Complete description"
    )
    prerequis_ids: List[int] = Field(
        default_factory=list, description="IDs of prerequisite AAVs"
    )
    prerequis_externes_codes: List[str] = Field(default_factory=list)
    code_prerequis_interdisciplinaire: Optional[str] = None
    type_evaluation: TypeEvaluationAAV

    @field_validator("libelle_integration")
    @classmethod
    def validate_libelle(cls, v: str) -> str:
        """Verify that the label can be integrated into a sentence."""
        phrase_test = f"We will work on {v}"
        if len(phrase_test) > 250:
            raise ValueError("Label too long for a fluent sentence")
        return v


class AAVCreate(AAVBase):
    """Model for creating an AAV (POST)."""
    id_aav: int = Field(..., gt=0, description="Unique identifier of the AAV")
    regles_progression: RegleProgression = Field(default_factory=RegleProgression)


class AAVUpdate(BaseModel):
    """Model for partial update (PATCH). All fields are optional."""
    nom: Optional[str] = Field(None, min_length=3, max_length=200)
    libelle_integration: Optional[str] = None
    description_markdown: Optional[str] = None
    prerequis_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None


class AAV(AAVBase):
    """Complete model of an AAV (API response)."""
    model_config = ConfigDict(from_attributes=True)

    id_aav: int
    is_active: bool = True
    version: int = 1
    created_at: datetime
    updated_at: datetime


# ============================================================
# MODELS FOR API RESPONSES
# ============================================================

class ErrorResponse(BaseModel):
    """Standard format for error responses."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="User-readable message")
    details: Optional[dict] = Field(
        None, description="Additional technical details"
    )
    timestamp: datetime = Field(default_factory=datetime.now)


class PaginatedResponse(BaseModel):
    """Standard format for paginated responses."""
    items: List[dict]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_previous: bool


class SuccessResponse(BaseModel):
    """Standard format for success confirmations."""
    success: bool = True
    message: str
    id: Optional[int] = None
    data: Optional[dict] = None


# ============================================================
# BUSINESS MODELS
# ============================================================

class MetriqueQualiteAAV(BaseModel):
    """Model for quality metrics of an AAV."""
    model_config = ConfigDict(from_attributes=True)

    id_metrique: Optional[int] = None
    id_aav: int
    score_covering_ressources: float
    taux_succes_moyen: float
    est_utilisable: bool
    nb_tentatives_total: int
    nb_apprenants_distincts: int
    ecart_type_scores: float
    date_calcul: datetime
    periode_debut: datetime
    periode_fin: datetime


class LearnerBase(BaseModel):
    """Base model for a learner."""
    model_config = ConfigDict(from_attributes=True)

    id_apprenant: int
    nom_utilisateur: str
    email: str
    date_inscription: datetime
    derniere_connexion: Optional[datetime] = None
    is_active: bool = True
    ontologie_reference_id: Optional[int] = None


class Rapport(BaseModel):
    """Model for reports."""
    model_config = ConfigDict(from_attributes=True)

    id_rapport: Optional[int] = None
    type_rapport: str
    id_cible: Union[str, int]
    periode_debut: Optional[datetime] = None
    periode_fin: Optional[datetime] = None
    format: str
    date_generation: datetime
    contenu: str
    format_fichier: str


class AlerteQualite(BaseModel):
    """Model for quality alerts."""
    model_config = ConfigDict(from_attributes=True)

    id_alerte: int
    type_alerte: str
    id_cible: int
    nom_cible: str
    severite: str
    description: str
    suggestions: List[str]
    date_detection: datetime
    statut: str


class Enseignant(BaseModel):
    """Model for a teacher."""
    model_config = ConfigDict(from_attributes=True)

    id_enseignant: Optional[int] = None
    nom: str
    email: str
    discipline: List[str]
    date_creation: Optional[datetime] = None


# ============================================================
# GROUP 4 MODELS (ACTIVITIES AND SESSIONS)
# ============================================================

class ActiviteCreate(BaseModel):
    """Model for creating an activity."""
    id_activite: Optional[int] = None
    nom: str
    description: Optional[str] = None
    type_activite: str
    ids_exercices_inclus: List[int]
    discipline: Optional[str] = None
    niveau_difficulte: Optional[str] = None
    duree_estimee_minutes: Optional[int] = None


class ActiviteUpdate(BaseModel):
    """Model for updating an activity."""
    nom: Optional[str] = None
    description: Optional[str] = None
    type_activite: Optional[str] = None
    ids_exercices_inclus: Optional[List[int]] = None
    discipline: Optional[str] = None
    niveau_difficulte: Optional[str] = None
    duree_estimee_minutes: Optional[str] = None


class SessionCreate(BaseModel):
    """Model for creating a session."""
    id_activite: int
    id_apprenant: int


class Attempt(BaseModel):
    """Model for a learner's attempt on an activity."""
    id_exercice: int
    response: str
    temps_resolution_secondes: int


# ============================================================
# MODELS FOR ALERTS
# ============================================================

class AAVDifficile(BaseModel):
    """Represents an AAV with abnormally low success rate."""
    id_aav: int = Field(..., description="Unique ID of the AAV")
    nom: str = Field(..., description="Name of the AAV")
    taux_succes: float = Field(..., ge=0.0, le=1.0, description="Average rate between 0 and 1")
    nb_tentatives: int = Field(..., ge=0, description="Total number of attempts")
    suggestion: str = Field(..., description="Pedagogical suggestion")


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
    """Represents a learner at risk."""
    id_apprenant: int
    nom: str
    progression: float
    aavs_bloques: int


# ============================================================
# MODELS FOR REPORTS
# ============================================================

class RapportResponse(BaseModel):
    """Complete model for a report (API response)."""
    type_rapport: str
    id_cible: Union[str, int]
    periode_debut: datetime
    periode_fin: datetime
    format: str
    date_generation: datetime
    contenu: str
    format_fichier: str


# ============================================================
# MODELS FOR COMPARISONS
# ============================================================

class AAVComparaison(BaseModel):
    """Model for comparison between AAVs."""
    id_aav: int
    nom: str
    taux_succes: float
    nb_tentatives: int
    nb_apprenants: int


class ApprenantComparaison(BaseModel):
    """Model for comparison between learners."""
    id_apprenant: int
    nom_utilisateur: str
    progression_globale: float
    aavs_maitrise: int
    aavs_encours: int


class RapportGlobalResponse(BaseModel):
    """Model for global report."""
    titre: str
    date_generation: datetime
    periode_debut: Optional[datetime] = None
    periode_fin: Optional[datetime] = None
    contenu: dict
    format: str


# ============================================================
# MODELS FOR DASHBOARD
# ============================================================

class OntologyCoverage(BaseModel):
    """Model for ontology coverage."""
    total_aavs: int
    aavs_actives: int
    aavs_inutilisees: int
    couverture_pourcentage: float
    disciplines_couvertes: List[str]


class TeacherDashboard(BaseModel):
    """Model for teacher dashboard."""
    id_enseignant: int
    nom: str
    aavs_geres: int
    apprenants_total: int
    taux_succes_moyen: float
    alertes_actives: int


class DisciplineDashboard(BaseModel):
    """Model for discipline dashboard."""
    discipline: str
    aavs_total: int
    taux_succes_moyen: float
    apprenants_engages: int
    activites_recentes: int


# ============================================================
# MODELS FOR REPORT REQUESTS
# ============================================================

class RapportRequest(BaseModel):
    """Model for report request."""
    type_rapport: str
    id_cible: Optional[int] = None
    format: str = "json"
    periode_debut: Optional[datetime] = None
    periode_fin: Optional[datetime] = None
