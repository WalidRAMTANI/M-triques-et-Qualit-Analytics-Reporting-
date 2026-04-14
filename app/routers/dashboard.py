from fastapi import APIRouter, HTTPException
from app.services.dashboard_data import get_teacher_stats, get_discipline_stats, get_ontology_cov
from app.model.schemas import OntologyCoverage, TeacherDashboard, DisciplineDashboard
router = APIRouter()

@router.get("/teachers/{id_enseignant}/overview", response_model=TeacherDashboard)
def get_teacher_dashboard(id_enseignant: int):
    """
    Récupère les statistiques du tableau de bord pour un enseignant spécifique.

    Args:
        id_enseignant (int): L'identifiant de l'enseignant.

    Returns:
        TeacherDashboard: Les statistiques (groupes, cours, alertes).

    Raises:
        HTTPException: 404 si aucune statistique n'est trouvée.
    """
    stats = get_teacher_stats(id_enseignant)
    if not stats:
        raise HTTPException(status_code=404, detail=f"Aucune statistique trouvée pour l'enseignant {id_enseignant}")
    return stats
@router.get("/discipline/{discipline}/stats", response_model=DisciplineDashboard)
def get_discipline_dashboard(discipline: str):
    """
    Récupère une vue d'ensemble des statistiques pour une discipline donnée.

    Args:
        discipline (str): Le nom de la discipline.

    Returns:
        DisciplineDashboard: Métriques agrégées pour la discipline.

    Raises:
        HTTPException: 404 si aucune donnée n'est trouvée.
    """
    stats = get_discipline_stats(discipline)
    if not stats:
        raise HTTPException(status_code=404, detail=f"Aucune statistique trouvée pour la discipline {discipline}")
    return DisciplineDashboard(**stats)
@router.get("/ontology/{id_reference}/coverage", response_model= OntologyCoverage)
def get_ontology_coverage(id_reference: int):
    """
    Calcule le taux de couverture d'une ontologie (progression globale du curriculum).

    Args:
        id_reference (int): L'identifiant de l'ontologie.

    Returns:
        OntologyCoverage: Métriques de couverture.

    Raises:
        HTTPException: 404 si l'ontologie ou ses données sont introuvables.
    """
    coverage = get_ontology_cov(id_reference)
    if not coverage:
        raise HTTPException(status_code=404, detail=f"Couverture introuvable pour l'ontologie {id_reference}")
    return coverage