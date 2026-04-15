# app/model/model.py
"""
Modèles de données et énumérations du projet.

NOTE: Les modèles Pydantic (pour les requêtes/réponses API) se trouvent dans :
    app/model/schemas.py

Les modèles SQLAlchemy ORM (pour la base de données) se trouvent dans :
    app/database.py
"""

# Import des énumérations depuis schemas pour compatibilité
from app.model.schemas import (
    TypeEvaluationAAV,
    TypeAAV,
    NiveauDifficulte,
    TypeActivite,
)

# Import des modèles Pydantic depuis schemas
from app.model.schemas import (
    # Énumérations
    # (déjà importées ci-dessus)
    # Modèles de base
    RegleProgression,
    AAVBase,
    AAVCreate,
    AAVUpdate,
    AAV,
    # Réponses API
    ErrorResponse,
    PaginatedResponse,
    SuccessResponse,
    # Modèles métier
    MetriqueQualiteAAV,
    LearnerBase,
    Rapport,
    AlerteQualite,
    Enseignant,
    # Groupe 4
    ActiviteCreate,
    ActiviteUpdate,
    SessionCreate,
    Attempt,
    # Alertes
    AAVDifficile,
    AAVInutilise,
    AAVFragile,
    ApprenantRisque,
    # Rapports
    RapportResponse,
    RapportRequest,
    # Comparaisons
    AAVComparaison,
    ApprenantComparaison,
    RapportGlobalResponse,
    # Dashboard
    OntologyCoverage,
    TeacherDashboard,
    DisciplineDashboard,
)

# ============================================================
# MODÈLES SQLALCHEMY ORM
# ============================================================
# NOTE: Tous les modèles SQLAlchemy ORM sont définis dans app/database.py
# pour éviter les boucles circulaires d'imports.
#
# Les modèles disponibles dans app/database.py :
#   - AAVModel
#   - OntologyReferenceModel
#   - ApprenantModel
#   - StatutApprentissageModel
#   - TentativeModel
#   - ActivitePedagogiqueModel
#   - SessionApprenantModel
#   - PromptFabricationAAVModel
#   - ExerciceInstanceModel
#   - DiagnosticRemediationModel
#   - MetriqueQualiteAAVModel
#   - AlerteQualiteModel
#   - RapportPeriodiqueModel
#   - EnseignantModel
#
# Exemple d'import :
#   from app.database import AAVModel, ApprenantModel
# ============================================================

__all__ = [
    # Énumérations
    "TypeEvaluationAAV",
    "TypeAAV",
    "NiveauDifficulte",
    "TypeActivite",
    # Modèles de base
    "RegleProgression",
    "AAVBase",
    "AAVCreate",
    "AAVUpdate",
    "AAV",
    # Réponses API
    "ErrorResponse",
    "PaginatedResponse",
    "SuccessResponse",
    # Modèles métier
    "MetriqueQualiteAAV",
    "LearnerBase",
    "Rapport",
    "AlerteQualite",
    "Enseignant",
    # Groupe 4
    "ActiviteCreate",
    "ActiviteUpdate",
    "SessionCreate",
    "Attempt",
    # Alertes
    "AAVDifficile",
    "AAVInutilise",
    "AAVFragile",
    "ApprenantRisque",
    # Rapports
    "RapportResponse",
    "RapportRequest",
    # Comparaisons
    "AAVComparaison",
    "ApprenantComparaison",
    "RapportGlobalResponse",
    # Dashboard
    "OntologyCoverage",
    "TeacherDashboard",
    "DisciplineDashboard",
]



# ---------------------------------- autre groupe

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Literal, Any
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
    """
    Règles déterminant comment un apprenant progresse sur un AAV.

    Exemple:
        - seuil_succes: 0.7 (70% pour réussir)
        - nombre_succes_consecutifs: 3 (3 réussites d'affilée = maîtrise)
    """
    seuil_succes: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Score minimum pour considérer une tentative comme réussie"
    )
    maitrise_requise: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Niveau de maîtrise à atteindre pour valider l'AAV"
    )
    nombre_succes_consecutifs: int = Field(
        default=1,
        ge=1,
        description="Nombre de réussites consécutives requises"
    )
    nombre_jugements_pairs_requis: int = Field(
        default=3,
        ge=1,
        description="Pour évaluation par les pairs: jugements nécessaires"
    )
    tolerance_jugement: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Marge de tolérance pour les évaluations par pairs"
    )

class AAVBase(BaseModel):
    """Champs de base pour un AAV (création et mise à jour)."""
    nom: str = Field(..., min_length=3, max_length=200, description="Nom technique de l'AAV")
    libelle_integration: str = Field(
        ...,
        min_length=5,
        description="Forme grammaticale pour insertion dans une phrase"
    )
    discipline: str = Field(..., min_length=2, description="Discipline (ex: Mathématiques)")
    enseignement: str = Field(..., description="Enseignement spécifique (ex: Algèbre)")
    type_aav: TypeAAV
    description_markdown: str = Field(..., min_length=10, description="Description complète")
    prerequis_ids: List[int] = Field(default_factory=list, description="IDs des AAV prérequis")
    prerequis_externes_codes: List[str] = Field(default_factory=list)
    code_prerequis_interdisciplinaire: Optional[str] = None
    type_evaluation: TypeEvaluationAAV

    @field_validator('libelle_integration')
    @classmethod
    def validate_libelle(cls, v: str) -> str:
        """Vérifie que le libellé peut s'intégrer dans une phrase."""
        phrase_test = f"Nous allons travailler {v}"
        if len(phrase_test) > 250:
            raise ValueError("Libellé trop long pour une phrase fluide")
        return v

class AAVCreate(AAVBase):
    """Modèle pour la création d'un AAV (POST)."""
    id_aav: int = Field(..., gt=0, description="Identifiant unique de l'AAV")
    regles_progression: RegleProgression = Field(default_factory=RegleProgression)

class AAVUpdate(BaseModel):
    """Modèle pour la mise à jour partielle (PATCH). Tous les champs sont optionnels."""
    nom: Optional[str] = Field(None, min_length=3, max_length=200)
    libelle_integration: Optional[str] = None
    description_markdown: Optional[str] = None
    prerequis_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None

class AAV(AAVBase):
    """Modèle complet d'un AAV (réponse API)."""
    id_aav: int
    is_active: bool = True
    version: int = 1
    created_at: datetime
    updated_at: datetime

    class Config:
        """Configuration Pydantic V2."""
        from_attributes = True  # Permet de créer depuis un objet SQLAlchemy/dict

# ============================================
# MODÈLES POUR LES RÉPONSES API
# ============================================

class ErrorResponse(BaseModel):
    """Format standard pour les réponses d'erreur."""
    error: str = Field(..., description="Type d'erreur")
    message: str = Field(..., description="Message lisible par l'utilisateur")
    details: Optional[dict] = Field(None, description="Détails techniques supplémentaires")
    timestamp: datetime = Field(default_factory=datetime.now)

class PaginatedResponse(BaseModel):
    """Format standard pour les réponses paginées."""
    items: List[dict]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_previous: bool

class SuccessResponse(BaseModel):
    """Format standard pour les confirmations de succès."""
    success: bool = True
    message: str
    id: Optional[int] = None
    data: Optional[dict] = None



#---------------- autre groupe
# app/models.py

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
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
    """
    Règles déterminant comment un apprenant progresse sur un AAV.

    Exemple:
        - seuil_succes: 0.7 (70% pour réussir)
        - nombre_succes_consecutifs: 3 (3 réussites d'affilée = maîtrise)
    """

    seuil_succes: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Score minimum pour considérer une tentative comme réussie"
    )
    maitrise_requise: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Niveau de maîtrise à atteindre pour valider l'AAV"
    )
    nombre_succes_consecutifs: int = Field(
        default=1,
        ge=1,
        description="Nombre de réussites consécutives requises"
    )
    nombre_jugements_pairs_requis: int = Field(
        default=3,
        ge=1,
        description="Pour évaluation par les pairs : jugements nécessaires"
    )
    tolerance_jugement: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Marge de tolérance pour les évaluations par pairs"
    )


class AAVBase(BaseModel):
    """Champs de base pour un AAV (création et mise à jour)."""

    nom: str = Field(
        ..., min_length=3, max_length=200,
        description="Nom technique de l'AAV"
    )
    libelle_integration: str = Field(
        ...,
        min_length=5,
        description="Forme grammaticale pour insertion dans une phrase"
    )
    discipline: str = Field(
        ..., min_length=2, description="Discipline (ex: Mathématiques)"
    )
    enseignement: str = Field(
        ..., description="Enseignement spécifique (ex: Algèbre)"
    )
    type_aav: TypeAAV
    description_markdown: str = Field(
        ..., min_length=10, description="Description complète"
    )
    prerequis_ids: List[int] = Field(
        default_factory=list, description="IDs des AAV prérequis"
    )
    prerequis_externes_codes: List[str] = Field(default_factory=list)
    code_prerequis_interdisciplinaire: Optional[str] = None
    type_evaluation: TypeEvaluationAAV

    @field_validator('libelle_integration')
    @classmethod
    def validate_libelle(cls, v: str) -> str:
        """Vérifie que le libellé peut s'intégrer dans une phrase."""
        phrase_test = f"Nous allons travailler {v}"
        if len(phrase_test) > 250:
            raise ValueError("Libellé trop long pour une phrase fluide")
        return v


class AAVCreate(AAVBase):
    """Modèle pour la création d'un AAV (POST)."""

    id_aav: int = Field(
        ..., gt=0, description="Identifiant unique de l'AAV"
    )
    regles_progression: RegleProgression = Field(
        default_factory=RegleProgression
    )


class AAVUpdate(BaseModel):
    """Modèle pour la mise à jour partielle (PATCH). Tous les champs optionnels."""

    nom: Optional[str] = Field(None, min_length=3, max_length=200)
    libelle_integration: Optional[str] = None
    description_markdown: Optional[str] = None
    prerequis_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None


class AAV(AAVBase):
    """Modèle complet d'un AAV (réponse API)."""

    id_aav: int
    is_active: bool = True
    version: int = 1
    created_at: datetime
    updated_at: datetime

    class Config:
        """Configuration Pydantic V2."""

        from_attributes = True


# ============================================
# MODÈLES POUR LES RÉPONSES API
# ============================================

class ErrorResponse(BaseModel):
    """Format standard pour les réponses d'erreur."""

    error: str = Field(..., description="Type d'erreur")
    message: str = Field(..., description="Message lisible par l'utilisateur")
    details: Optional[dict] = Field(None, description="Détails techniques")
    timestamp: datetime = Field(default_factory=datetime.now)


class PaginatedResponse(BaseModel):
    """Format standard pour les réponses paginées."""

    items: List[dict]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_previous: bool


class SuccessResponse(BaseModel):
    """Format standard pour les confirmations de succès."""

    success: bool = True
    message: str
    id: Optional[int] = None
    data: Optional[dict] = None


# ============================================
# MODÈLES GROUPE 8 : Génération d'Exercices
# ============================================

class PromptFabricationAAV(BaseModel):
    """Modèle complet d'un prompt de fabrication (réponse API)."""

    id_prompt: int
    cible_aav_id: int
    type_exercice_genere: Optional[TypeEvaluationAAV] = None
    prompt_texte: str
    version_prompt: int = 1
    created_by: Optional[int] = None
    date_creation: Optional[datetime] = None
    is_active: bool = True
    meta_data: Optional[Any] = None

    class Config:
        from_attributes = True


class PromptCreate(BaseModel):
    """Modèle pour la création d'un prompt (POST)."""

    cible_aav_id: int = Field(..., gt=0, description="ID de l'AAV cible")
    type_exercice_genere: Optional[TypeEvaluationAAV] = None
    prompt_texte: str = Field(..., min_length=10, description="Texte du prompt")
    version_prompt: int = Field(default=1, ge=1)
    created_by: Optional[int] = None
    is_active: bool = True
    meta_data: Optional[str] = None


class PromptUpdate(BaseModel):
    """Modèle pour la mise à jour partielle d'un prompt (PATCH)."""

    cible_aav_id: Optional[int] = None
    type_exercice_genere: Optional[TypeEvaluationAAV] = None
    prompt_texte: Optional[str] = None
    version_prompt: Optional[int] = None
    is_active: Optional[bool] = None
    meta_data: Optional[str] = None


class StrategieSelection(str, Enum):
    """Stratégies de sélection d'exercices."""

    ADAPTIVE = "adaptive"
    RANDOM = "random"
    PROGRESSIVE = "progressive"


class SelectionExercicesRequest(BaseModel):
    """Body pour POST /exercises/select."""

    id_apprenant: int = Field(..., gt=0, description="ID de l'apprenant")
    id_aavs_cibles: List[int] = Field(
        ..., min_length=1, description="Liste des AAV ciblés"
    )
    nombre_exercices: int = Field(default=5, ge=1, le=50)
    strategie: StrategieSelection = StrategieSelection.ADAPTIVE


class SequenceExercicesRequest(BaseModel):
    """Body pour POST /exercises/sequence."""

    id_apprenant: int = Field(..., gt=0)
    id_aavs_cibles: List[int] = Field(..., min_length=1)
    nombre_exercices: int = Field(default=5, ge=1, le=50)


class PreviewPromptRequest(BaseModel):
    """Body pour POST /prompts/{id_prompt}/preview."""

    id_apprenant: int = Field(
        ..., gt=0, description="ID de l'apprenant pour contextualiser"
    )
    include_context: bool = Field(
        default=True, description="Inclure le contexte complet"
    )


class EvaluationRequest(BaseModel):
    """Body pour POST /exercises/evaluate."""

    id_exercice: int = Field(..., gt=0)
    reponse_apprenant: str = Field(..., min_length=1)
    type_evaluation: TypeEvaluationAAV = TypeEvaluationAAV.CALCUL


class SimulateResponseRequest(BaseModel):
    """Body pour POST /exercises/simulate-response."""

    id_apprenant: int = Field(..., gt=0, description="ID de l'apprenant simulé")
    id_aav: int = Field(..., gt=0, description="AAV ciblé par la simulation")
    nb_tentatives: int = Field(
        default=5, ge=1, le=50,
        description="Nombre de réponses à simuler"
    )
    profil: str = Field(
        default="aleatoire",
        description=(
            "Profil de l'apprenant simulé : "
            "'bon', 'moyen', 'faible', 'aleatoire'"
        )
    )


# -------- autre groupe 
# app/models.py

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Literal, Any
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
    """
    Règles déterminant comment un apprenant progresse sur un AAV.

    Exemple:
        - seuil_succes: 0.7 (70% pour réussir)
        - nombre_succes_consecutifs: 3 (3 réussites d'affilée = maîtrise)
    """
    seuil_succes: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Score minimum pour considérer une tentative comme réussie"
    )
    maitrise_requise: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Niveau de maîtrise à atteindre pour valider l'AAV"
    )
    nombre_succes_consecutifs: int = Field(
        default=1,
        ge=1,
        description="Nombre de réussites consécutives requises"
    )
    nombre_jugements_pairs_requis: int = Field(
        default=3,
        ge=1,
        description="Pour évaluation par les pairs: jugements nécessaires"
    )
    tolerance_jugement: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Marge de tolérance pour les évaluations par pairs"
    )

class AAVBase(BaseModel):
    """Champs de base pour un AAV (création et mise à jour)."""
    nom: str = Field(..., min_length=3, max_length=200, description="Nom technique de l'AAV")
    libelle_integration: str = Field(
        ...,
        min_length=5,
        description="Forme grammaticale pour insertion dans une phrase"
    )
    discipline: str = Field(..., min_length=2, description="Discipline (ex: Mathématiques)")
    enseignement: str = Field(..., description="Enseignement spécifique (ex: Algèbre)")
    type_aav: TypeAAV
    description_markdown: str = Field(..., min_length=10, description="Description complète")
    prerequis_ids: List[int] = Field(default_factory=list, description="IDs des AAV prérequis")
    prerequis_externes_codes: List[str] = Field(default_factory=list)
    code_prerequis_interdisciplinaire: Optional[str] = None
    type_evaluation: TypeEvaluationAAV

    @field_validator('libelle_integration')
    @classmethod
    def validate_libelle(cls, v: str) -> str:
        """Vérifie que le libellé peut s'intégrer dans une phrase."""
        phrase_test = f"Nous allons travailler {v}"
        if len(phrase_test) > 250:
            raise ValueError("Libellé trop long pour une phrase fluide")
        return v

class AAVCreate(AAVBase):
    """Modèle pour la création d'un AAV (POST)."""
    id_aav: int = Field(..., gt=0, description="Identifiant unique de l'AAV")
    regles_progression: RegleProgression = Field(default_factory=RegleProgression)

class AAVUpdate(BaseModel):
    """Modèle pour la mise à jour partielle (PATCH). Tous les champs sont optionnels."""
    nom: Optional[str] = Field(None, min_length=3, max_length=200)
    libelle_integration: Optional[str] = None
    description_markdown: Optional[str] = None
    prerequis_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None

class AAV(AAVBase):
    """Modèle complet d'un AAV (réponse API)."""
    id_aav: int
    is_active: bool = True
    version: int = 1
    created_at: datetime
    updated_at: datetime

    class Config:
        """Configuration Pydantic V2."""
        from_attributes = True  # Permet de créer depuis un objet SQLAlchemy/dict

# ============================================
# MODÈLES POUR LES RÉPONSES API
# ============================================

class ErrorResponse(BaseModel):
    """Format standard pour les réponses d'erreur."""
    error: str = Field(..., description="Type d'erreur")
    message: str = Field(..., description="Message lisible par l'utilisateur")
    details: Optional[dict] = Field(None, description="Détails techniques supplémentaires")
    timestamp: datetime = Field(default_factory=datetime.now)

class PaginatedResponse(BaseModel):
    """Format standard pour les réponses paginées."""
    items: List[dict]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_previous: bool

class SuccessResponse(BaseModel):
    """Format standard pour les confirmations de succès."""
    success: bool = True
    message: str
    id: Optional[int] = None
    data: Optional[dict] = None
    
# ============================================
# MODÈLES GROUPE 6: REMÉDIATION // POST du cahier de charges
# ============================================

class TriggerRemediation(BaseModel):
    """Méthode pour déclencher une analyse de remédiation."""
    id_apprenant: int = Field(..., description="ID de l'apprenant")
    id_aav_source: int = Field(..., description="ID de l'AAV de l'échec")
    score_obtenu: float = Field(..., ge=0.0, le=1.0, description="Score de l'apprenant")
    type_echec: Literal["calcul","comprehension","prerequis_manquant"] = Field(..., description="Détail de l'échec")
    
class GeneratePath(BaseModel):
    """Méthode pour générer un parcours personnalisé."""
    id_apprenant: int
    id_aav_cible: int
    profondeur_max: int = Field(default=3, ge=1, le=10, description="Profondeur max de l'analyse")
    
class RemediationResponse(BaseModel):
    """Format standard pour la réponse d'une analyse"""
    id_diagnostic: int
    id_apprenant: int
    id_aav_source: int
    aav_defaillants: List[int]
    recommandations: List[dict]
    date_diagnostic: datetime
    
class PathRequest(BaseModel):
    """Méthode pour demander l'analyse d'une séquence d'AVV"""
    id_apprenant: int
    chemin_aavs: List[int] = Field(..., description="AVVs à analyser")
    
class ErreurApprenant(BaseModel):
    """Format standard pour la réponse d'une analyse sur le niveau de l'apprenant sur un AVV"""
    id_aav: int
    maitrise: float
    reussi: bool
    
#--- autre groupe 
# Moàdèles Pydantic

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
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
    """
    Règles déterminant comment un apprenant progresse sur un AAV.

    Exemple:
        - seuil_succes: 0.7 (70% pour réussir)
        - nombre_succes_consecutifs: 3 (3 réussites d'affilée = maîtrise)
    """
    seuil_succes: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Score minimum pour considérer une tentative comme réussie"
    )
    maitrise_requise: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Niveau de maîtrise à atteindre pour valider l'AAV"
    )
    nombre_succes_consecutifs: int = Field(
        default=1,
        ge=1,
        description="Nombre de réussites consécutives requises"
    )
    nombre_jugements_pairs_requis: int = Field(
        default=3,
        ge=1,
        description="Pour évaluation par les pairs: jugements nécessaires"
    )
    tolerance_jugement: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Marge de tolérance pour les évaluations par pairs"
    )


class AAVBase(BaseModel):
    """Champs de base pour un AAV (création et mise à jour)."""
    nom: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Nom technique de l'AAV")
    libelle_integration: str = Field(
        ...,
        min_length=5,
        description="Forme grammaticale pour insertion dans une phrase"
    )
    discipline: str = Field(
        ...,
        min_length=2,
        description="Discipline (ex: Mathématiques)")
    enseignement: str = Field(
        ...,
        description="Enseignement spécifique (ex: Algèbre)")
    type_aav: TypeAAV
    description_markdown: str = Field(
        ...,
        min_length=10,
        description="Description complète")
    prerequis_ids: List[int] = Field(
        default_factory=list,
        description="IDs des AAV prérequis")
    prerequis_externes_codes: List[str] = Field(default_factory=list)
    code_prerequis_interdisciplinaire: Optional[str] = None
    type_evaluation: TypeEvaluationAAV

    @field_validator('libelle_integration')
    @classmethod
    def validate_libelle(cls, v: str) -> str:
        """Vérifie que le libellé peut s'intégrer dans une phrase."""
        phrase_test = f"Nous allons travailler {v}"
        if len(phrase_test) > 250:
            raise ValueError("Libellé trop long pour une phrase fluide")
        return v

    @field_validator(
        'prerequis_ids',
        'prerequis_externes_codes',
        mode='before')
    @classmethod
    def parse_json_list(cls, v):
        """Convertit automatiquement les strings JSON en listes."""
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except BaseException:
                return []
        return v or []


class AAVCreate(AAVBase):
    """Modèle pour la création d'un AAV (POST)."""
    id_aav: int = Field(...,
                        gt=0,
                        description="Identifiant unique de l'AAV")
    regles_progression: RegleProgression = Field(
        default_factory=RegleProgression)


class AAVUpdate(BaseModel):
    """
    Modèle pour la mise à jour partielle (PATCH).
    Tous les champs sont optionnels.
    """
    nom: Optional[str] = Field(None, min_length=3, max_length=200)
    libelle_integration: Optional[str] = None
    description_markdown: Optional[str] = None
    prerequis_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None


class AAV(AAVBase):
    """Modèle complet d'un AAV (réponse API)."""
    id_aav: int
    is_active: bool = True
    version: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator('created_at', 'updated_at', mode='before')
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v)
            except BaseException:
                return None
        return v


class LearnerBase(BaseModel):  # ?voir quoi retirer
    id_apprenant: int = Field(..., gt=0)
    nom_utilisateur: str = Field(..., min_length=1,
                                 description="Nom de l'apprenti")
    email: str = Field(description="E-mail de l'apprenti")
    # Car on veux pouvoir accepter None
    ontologie_reference_id: Optional[int] = None
    statuts_actifs_ids: List[int] = Field(default_factory=list)
    codes_prerequis_externes_valides: List[str] = Field(default_factory=list)
    date_inscription: Optional[datetime] = None
    derniere_connexion: Optional[datetime] = None
    is_active: bool = True  # on met a True direct et on changera au cas ou

    @field_validator('email')
    @classmethod
    def test_email_valide(cls, value: str) -> str:
        if '@' not in value or '.' not in value.split(
                '@')[-1]:  # comme ça on autorise les .fr .org etc
            raise ValueError(
                "Invalid email format (supposed to be exemple@xyz.com)")
        return value.lower()

    @field_validator('statuts_actifs_ids',
                     'codes_prerequis_externes_valides',
                     mode='before')
    @classmethod
    def parse_json_list(cls, v):
        """Convertit automatiquement les strings JSON en listes."""
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except BaseException:
                return []
        return v or []


class LearnerCreate(LearnerBase):  # ? rajouter les choses retirées
    id_apprenant: Optional[int] = None


class LearnerUpdate(BaseModel):
    """
    Schema de mise a jour partielle d'un profil apprenant.

    Tous les champs sont optionnels : seuls les champs fournis sont modifies.
    """
    nom_utilisateur: Optional[str] = None
    email: Optional[str] = None
    ontologie_reference_id: Optional[int] = None
    statuts_actifs_ids: Optional[List[int]] = None
    codes_prerequis_externes_valides: Optional[List[str]] = None


class Learner(LearnerBase):  # ? a rajouter
    model_config = ConfigDict(from_attributes=True)


# ============================================
# MODÈLES POUR LES RÉPONSES API
# ============================================

class ErrorResponse(BaseModel):
    """Format standard pour les réponses d'erreur."""
    error: str = Field(..., description="Type d'erreur")
    message: str = Field(..., description="Message lisible par l'utilisateur")
    details: Optional[dict] = Field(
        None, description="Détails techniques supplémentaires")
    timestamp: datetime = Field(default_factory=datetime.now)


class PaginatedResponse(BaseModel):
    """Format standard pour les réponses paginées."""
    items: List[dict]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_previous: bool


class SuccessResponse(BaseModel):
    """Format standard pour les confirmations de succès."""
    success: bool = True
    message: str
    id: Optional[int] = None
    data: Optional[dict] = None

# ============================================
# MODÈLES : External Prerequisite Validation
# ============================================


class ExternalPrerequisiteBase(BaseModel):
    code_prerequis: str = Field(..., min_length=1,
                                description="Code du prérequis externe")
    validated_by: Optional[str] = Field(
        None, description="Qui a validé le prérequis")
    notes: Optional[float] = Field(
        None, ge=0, description="Score de validation")


class ExternalPrerequisiteCreate(ExternalPrerequisiteBase):
    pass


class ExternalPrerequisite(ExternalPrerequisiteBase):
    id_apprenant: int
    validated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# ============================================
# MODÈLES : Statuts d'Apprentissage
# ============================================


class LearningStatus(BaseModel):
    id: int
    id_apprenant: int
    id_aav_cible: int
    niveau_maitrise: float = Field(ge=0.0, le=1.0)
    historique_tentatives_ids: List[int] = Field(default_factory=list)
    date_debut_apprentissage: Optional[datetime] = None
    date_derniere_session: Optional[datetime] = None
    est_maitrise: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def validate_maitrise(self) -> 'LearningStatus':
        if self.est_maitrise is None:
             self.est_maitrise = False
        return self

    @field_validator('historique_tentatives_ids', mode='before')
    @classmethod
    def parse_json(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except BaseException:
                return []
        if isinstance(v, list):
            return v
        return v or []


class LearningStatusSummary(BaseModel):
    id_apprenant: int
    total: int
    maitrise: int                # niveau_maitrise >= 0.9
    en_cours: int                # 0 < niveau_maitrise < 0.9
    non_commence: int            # niveau_maitrise == 0
    taux_maitrise_global: float  # maitrise / total en %

# ============================================
# MODÈLES : Ontologie
# ============================================


class OntologyReference(BaseModel):
    id_reference: int
    discipline: str
    aavs_ids_actifs: List[int] = Field(default_factory=list)
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator('aavs_ids_actifs', mode='before')
    @classmethod
    def parse_json(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except BaseException:
                return []
        return v or []


class OntologySwitchResponse(BaseModel):
    success: bool
    message: str
    id_apprenant: int
    ancienne_ontologie_id: Optional[int]
    nouvelle_ontologie_id: int

# ============================================
# MODÈLES : Progression
# ============================================


class ProgressResponse(BaseModel):
    id_apprenant: int
    ontologie_reference_id: int
    total_aavs: int
    aavs_maitrise: int
    taux_progression: float  # en pourcentage


#------ autre groupe 
# app/models.py

from pydantic import BaseModel, Field, field_validator, model_validator # type: ignore
from typing import Optional, List, Literal, Any
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
    """
    Règles déterminant comment un apprenant progresse sur un AAV.

    Exemple:
        - seuil_succes: 0.7 (70% pour réussir)
        - nombre_succes_consecutifs: 3 (3 réussites d'affilée = maîtrise)
    """
    seuil_succes: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Score minimum pour considérer une tentative comme réussie"
    )
    maitrise_requise: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Niveau de maîtrise à atteindre pour valider l'AAV"
    )
    nombre_succes_consecutifs: int = Field(
        default=1,
        ge=1,
        description="Nombre de réussites consécutives requises"
    )
    nombre_jugements_pairs_requis: int = Field(
        default=3,
        ge=1,
        description="Pour évaluation par les pairs: jugements nécessaires"
    )
    tolerance_jugement: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Marge de tolérance pour les évaluations par pairs"
    )

class AAVBase(BaseModel):
    """Champs de base pour un AAV (création et mise à jour)."""
    nom: str = Field(..., min_length=3, max_length=200, description="Nom technique de l'AAV")
    libelle_integration: str = Field(
        ...,
        min_length=5,
        description="Forme grammaticale pour insertion dans une phrase"
    )
    discipline: str = Field(..., min_length=2, description="Discipline (ex: Mathématiques)")
    enseignement: str = Field(..., description="Enseignement spécifique (ex: Algèbre)")
    type_aav: TypeAAV
    description_markdown: str = Field(..., min_length=10, description="Description complète")
    prerequis_ids: List[int] = Field(default_factory=list, description="IDs des AAV prérequis")
    prerequis_externes_codes: List[str] = Field(default_factory=list)
    code_prerequis_interdisciplinaire: Optional[str] = None
    type_evaluation: TypeEvaluationAAV

    @field_validator('libelle_integration')
    @classmethod
    def validate_libelle(cls, v: str) -> str:
        """Vérifie que le libellé peut s'intégrer dans une phrase."""
        phrase_test = f"Nous allons travailler {v}"
        if len(phrase_test) > 250:
            raise ValueError("Libellé trop long pour une phrase fluide")
        return v

class AAVCreate(AAVBase):
    """Modèle pour la création d'un AAV (POST)."""
    id_aav: int = Field(..., gt=0, description="Identifiant unique de l'AAV")
    regles_progression: RegleProgression = Field(default_factory=RegleProgression)

class AAVUpdate(BaseModel):
    """Modèle pour la mise à jour partielle (PATCH). Tous les champs sont optionnels."""
    nom: Optional[str] = Field(None, min_length=3, max_length=200)
    libelle_integration: Optional[str] = None
    description_markdown: Optional[str] = None
    prerequis_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None

class AAV(AAVBase):
    """Modèle complet d'un AAV (réponse API)."""
    id_aav: int
    is_active: bool = True
    version: int = 1
    created_at: datetime
    updated_at: datetime

    class Config:
        """Configuration Pydantic V2."""
        from_attributes = True  # Permet de créer depuis un objet SQLAlchemy/dict

# ============================================
# MODÈLES POUR LES RÉPONSES API
# ============================================

class ErrorResponse(BaseModel):
    """Format standard pour les réponses d'erreur."""
    error: str = Field(..., description="Type d'erreur")
    message: str = Field(..., description="Message lisible par l'utilisateur")
    details: Optional[dict] = Field(None, description="Détails techniques supplémentaires")
    timestamp: datetime = Field(default_factory=datetime.now)

class PaginatedResponse(BaseModel):
    """Format standard pour les réponses paginées."""
    items: List[dict]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_previous: bool

class SuccessResponse(BaseModel):
    """Format standard pour les confirmations de succès."""
    success: bool = True
    message: str
    id: Optional[int] = None
    data: Optional[dict] = None


# ============================================
# MODÈLES GROUPE 3 STATUT & TENTATIVES (faut qu'on se référence aux fichiers database.py pour les colonnes des tables et pas au fichier groupe3_statuts_tentatives.md passke y a pas les mêmes choses mais faut écouter database.py)
# ============================================

# ============================================
# MODÈLES POUR LES STATUTS D'APPRENTISSAGES
# ============================================

class StatutApprentissageCreate(BaseModel):
    """Modèle pour la création d'un statut d'apprentissage (POST)."""
    id_apprenant: int = Field(..., gt=0, description="Identifiant de l'apprenant")
    id_aav_cible: int = Field(..., gt=0, description="Identifiant de l'AAV cible")
    niveau_maitrise: float = Field(default=0.0, ge=0.0, le=1.0, description="Niveau de maîtrise actuel")
    historique_tentatives_ids: List[int] = Field(default_factory=list, description="Tableau des IDs des tentatives passées au format JSON")

class StatutApprentissageUpdate(BaseModel):
    """Modèle pour la mise à jour d'un statut d'apprentissage (PUT)."""
    niveau_maitrise: Optional[float] = Field(None, ge=0.0, le=1.0, description="Nouveau niveau de maîtrise")
    historique_tentatives_ids: Optional[List[int]] = Field(None, description="Nouveau tableau des IDs des tentatives passées au format JSON")

class StatutApprentissageMasteryUpdate(BaseModel):
    """Modèle pour la mise à jour du niveau de maîtrise d'un statut d'apprentissage (PUT)."""
    niveau_maitrise: float = Field(..., ge=0.0, le=1.0, description="Nouveau niveau de maîtrise")

class StatutApprentissage(BaseModel):
    """Modèle complet d'un statut d'apprentissage (réponse API)."""
    id: int
    id_apprenant: int
    id_aav_cible: int
    niveau_maitrise: float
    historique_tentatives_ids: List[int] = []
    date_debut_apprentissage: datetime
    date_derniere_session: Optional[datetime] = None
    est_maitrise: Optional[bool] = False

    class Config:
        """Configuration Pydantic V2."""
        from_attributes = True

# ============================================
# MODÈLES POUR LES TENTATIVES D'ÉVALUATION
# ============================================

class TentativeCreate(BaseModel):
    """Modèle pour la création d'une tentative d'évaluation d'un AAV (POST)."""
    id_exercice_ou_evenement: int = Field(..., gt=0, description="Identifiant de l'exercice ou de l'événement évalué")
    id_apprenant: int = Field(..., gt=0, description="Identifiant de l'apprenant")
    id_aav_cible: int = Field(..., gt=0, description="Identifiant de l'AAV cible")
    score_obtenu: float = Field(..., ge=0.0, le=1.0, description="Score obtenu lors de la tentative")
    est_valide: bool = Field(default=True, description="Indique si la tentative est valide selon les règles de progressions")
    temps_resolution_secondes: Optional[int] = Field(None, ge=0, description="Temps de résolution en secondes")
    meta_data: Optional[dict] = Field(None, description="Infos supplémentaires sur la tentative au format JSON")

    @field_validator('score_obtenu')
    @classmethod
    def arrondir_score(cls, x: float) -> float:
        """
        Arrondit le score à deux chiffres après la virgule

        Args:
            values (float): Le score à arrondir

        Returns:
            float: Le score arrondi à deux chiffres après la virgule
        """
        return round(x, 2)

class Tentative(TentativeCreate):
    """Modèle complet d'une tentative d'évaluation d'un AAV (réponse API)."""
    id: int
    id_exercice_ou_evenement: int
    id_apprenant: int
    id_aav_cible: int
    score_obtenu: float
    date_tentative: datetime
    est_valide: bool
    temps_resolution_secondes: Optional[int] = None
    meta_data: Optional[dict] = None

    class Config:
        """Configuration Pydantic V2."""
        from_attributes = True

class Process(BaseModel):
    """Modèle pour raitement d'une tentative (POST /attempts/{id}/process)."""
    tentative_id: int = Field(..., gt=0, description="Identifiant de la tentative traiter")
    id_apprenant: int = Field(..., gt=0, description="Identifiant de l'apprenant")
    id_aav_cible: int = Field(..., gt=0, description="Identifiant de l'AAV cible")
    ancien_niveau: float = Field(..., ge=0.0, le=1.0, description="Niveau de maîtrise avant la tentative")
    nouveau_niveau: float = Field(..., ge=0.0, le=1.0, description="Niveau de maîtrise après la tentative")
    est_maitrise: bool = Field(..., description="Indique si l'apprenant a réussi à maîtriser l'AAV après cette tentative")
    message: str = Field(..., description="Message de retour pour l'apprenant") # Est ce que on met ce champ en optionnel ou pas à voir ?
