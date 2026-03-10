from fastapi import APIRouter
from starlette.exceptions import HTTPException as StarletteHTTPException
from services.dashboard_data import get_teacher_stats, get_discipline_stats, get_ontology_cov
from schemas import OntologyCoverage, TeacherDashboard, DisciplineDashboard
router = APIRouter()

@router.get("/teachers/{id_enseignant}/{discipline}/overview", response_model=TeacherDashboard)
def get_teacher_dashboard(id_enseignant: str, discipline: str):
    return get_teacher_stats(id_enseignant, discipline);

@router.get("/discipline/{discipline}/stats", response_model=DisciplineDashboard)
def get_discipline_dashboard(discipline: str):
    return get_discipline_stats(discipline);

@router.get("/ontology/{id_reference}/coverage", response_model= OntologyCoverage)
def get_ontology_coverage(id_reference: int):
    coverage = get_ontology_cov(id_reference)
    return coverage