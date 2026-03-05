import fastapi
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from services.alert_detector import detecter_aavs_difficiles, detecter_aavs_inutilises, detecter_aavs_fragiles, detecter_apprenants_risque
from schemas import AAVDifficile, AAVInutilise, AAVFragile, ApprenantRisque

router = APIRouter()

# GET /alerts/difficult-aavs  - AAV avec taux de succès anormalement bas
# GET /alerts/unused-aavs     - AAV jamais ou rarement utilisés
# GET /alerts/fragile-aavs    - AAV avec forte variance dans les résultats
# GET /alerts/students-at-risk - Apprenants en difficulté

@router.get("/difficult-aavs", response_model=List[AAVDifficile])
def get_difficult_aavs() -> List[AAVDifficile]:
    """Récupère les AAV avec un taux de succès trop bas."""
    return detecter_aavs_difficiles()

@router.get("/unused-aavs", response_model=List[AAVInutilise])
def get_unused_aavs() -> List[AAVInutilise]:
    """Récupère les AAV jamais utilisés."""
    return detecter_aavs_inutilises()

@router.get("/fragile-aavs", response_model=List[AAVFragile])
def get_fragile_aavs() -> List[AAVFragile]:
    """Récupère les AAV avec des résultats très variables."""
    return detecter_aavs_fragiles()

@router.get("/students-at-risk", response_model=List[ApprenantRisque])
def get_students_at_risk(id_ontologie: int) -> List[ApprenantRisque]:
    """Récupère les apprenants en difficulté."""
    return detecter_apprenants_risque(id_ontologie)