from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, List, Literal, Union
from enum import Enum
from datetime import datetime

# ============================================
# ÉNUMÉRATIONS
# ============================================

class TypeEvaluationAAV(str, Enum):
    """Types d'évaluation possibles pour un AAV."""
    HUMAINE = "Humaine"
    CALCUL = "Calcul Automatisé"
    CHUTE = "Compréhension par Chute"
    INVENTION = "Validation par Invention"
    CRITIQUE = "Exercice de Critique"
    EVALUATION_PAIRS = "Évaluation par les Pairs"
    EVALUATION_AGREGEE = "Agrégation (Composite)"

class TypeAAV(str, Enum):
    """Types d'AAV possibles."""
    ATOMIQUE = "Atomique"
    COMPOSITE = "Composite (Chapitre)"

class NiveauDifficulte(str, Enum):
    """Niveaux de difficulté pour les exercices."""
    DEBUTANT = "debutant"
    INTERMEDIAIRE = "intermediaire"
    AVANCE = "avance"

# ============================================
# MODÈLES DE BASE (Communs à tous les groupes)
# ============================================

class RegleProgression(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    seuil_succes: float = Field(default=0.7, ge=0.0, le=1.0)
    maitrise_requise: float = Field(default=1.0, ge=0.0, le=1.0)
    nombre_succes_consecutifs: int = Field(default=1, ge=1)
    nombre_jugements_pairs_requis: int = Field(default=3, ge=1)
    tolerance_jugement: float = Field(default=0.2, ge=0.0, le=1.0)

class AAVBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    nom: str = Field(..., min_length=3, max_length=200)
    libelle_integration: str = Field(..., min_length=5)
    discipline: str = Field(..., min_length=2)
    enseignement: str = Field(..., min_length=2)
    type_aav: TypeAAV
    description_markdown: str = Field(..., min_length=10)
    prerequis_ids: List[int] = Field(default_factory=list)
    prerequis_externes_codes: List[str] = Field(default_factory=list)
    code_prerequis_interdisciplinaire: Optional[str] = None
    type_evaluation: TypeEvaluationAAV

    @field_validator('libelle_integration')
    @classmethod
    def validate_libelle(cls, v: str) -> str:
        if v and len(v) > 250:
            raise ValueError("Libellé trop long")
        return v

class AAVCreate(AAVBase):
    id_aav: int = Field(..., gt=0)
    regles_progression: RegleProgression = Field(default_factory=RegleProgression)

class AAVUpdate(BaseModel):
    nom: Optional[str] = Field(None, min_length=3, max_length=200)
    libelle_integration: Optional[str] = None
    description_markdown: Optional[str] = None
    prerequis_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None

class AAV(AAVBase):
    id_aav: int
    is_active: bool = True
    version: int = 1
    created_at: datetime
    updated_at: datetime

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_previous: bool

class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    id: Optional[int] = None
    data: Optional[dict] = None

# ------------------------------------------------------------------------#
class MetriqueQualiteAAV(BaseModel):
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
    model_config = ConfigDict(from_attributes=True)
    id_apprenant: int
    nom_utilisateur: str
    email: str
    date_inscription: datetime
    derniere_connexion: Optional[datetime] = None
    is_active: bool = True
    ontologie_reference_id: Optional[int] = None

class Rapport(BaseModel):
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
    model_config = ConfigDict(from_attributes=True)
    id_enseignant: Optional[int] = None
    nom: str
    email: str
    discipline: List[str]
    date_creation: Optional[datetime] = None