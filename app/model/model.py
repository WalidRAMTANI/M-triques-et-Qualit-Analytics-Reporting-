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
