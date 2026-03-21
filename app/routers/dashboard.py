from fastapi import APIRouter, HTTPException
from app.services.dashboard_data import get_teacher_stats, get_discipline_stats, get_ontology_cov
from app.model.schemas import OntologyCoverage, TeacherDashboard, DisciplineDashboard
router = APIRouter()

@router.get("/teachers/{id_enseignant}/overview", response_model=TeacherDashboard)
def get_teacher_dashboard(id_enseignant: str):
    """Retrieves dashboard statistics for a specific teacher."""
    stats = get_teacher_stats(id_enseignant)
    if not stats:
        raise HTTPException(status_code=404, detail=f"Aucune statistique trouvée pour l'enseignant {id_enseignant}")
    return stats
@router.get("/discipline/{discipline}/stats", response_model=DisciplineDashboard)
def get_discipline_dashboard(discipline: str):
    """Retrieves dashboard overview statistics for a discipline."""
    stats = get_discipline_stats(discipline)
    if not stats:
        raise HTTPException(status_code=404, detail=f"Aucune statistique trouvée pour la discipline {discipline}")
    return DisciplineDashboard(**stats)
@router.get("/ontology/{id_reference}/coverage", response_model= OntologyCoverage)
def get_ontology_coverage(id_reference: int):
    """Retrieves coverage metrics for a specific ontology (curriculum)."""
    coverage = get_ontology_cov(id_reference)
    if not coverage:
        raise HTTPException(status_code=404, detail=f"Couverture introuvable pour l'ontologie {id_reference}")
    return coverage