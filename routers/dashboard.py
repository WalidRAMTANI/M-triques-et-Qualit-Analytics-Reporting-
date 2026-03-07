from fastapi import APIRouter
from starlette.exceptions import HTTPException as StarletteHTTPException
from services.dashboard_data import get_teacher_stats, get_discipline_stats
from schemas import TeacherDashboard, DisciplineDashboard
router = APIRouter()

@router.get("/teachers/{id_enseignant}/overview", response_model=TeacherDashboard)
def get_teacher_dashboard(id_enseignant: str):
    return get_teacher_stats(id_enseignant);

@router.get("/discipline/{discipline}/stats", response_model=DisciplineDashboard)
def get_discipline_dashboard(discipline: str):
    return get_discipline_stats(discipline);