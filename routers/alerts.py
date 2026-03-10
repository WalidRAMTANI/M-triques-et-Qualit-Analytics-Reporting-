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
    
    aavs_difficiles = detecter_aavs_difficiles()
    if not aavs_difficiles:
        raise HTTPException(status_code=404, detail="Aucun AAV difficile détecté.")
    return aavs_difficiles
    
@router.get("/unused-aavs", response_model=List[AAVInutilise])
def get_unused_aavs() -> List[AAVInutilise]:
    """Récupère les AAV jamais utilisés."""
    aavs_inutilises = detecter_aavs_inutilises()
    if not aavs_inutilises:
        raise HTTPException(status_code=404, detail="Aucun AAV inutilisé détecté.")
    return aavs_inutilises

@router.get("/fragile-aavs", response_model=List[AAVFragile])
def get_fragile_aavs() -> List[AAVFragile]:
    """Récupère les AAV avec des résultats très variables."""
    aavs_fragiles = detecter_aavs_fragiles()
    if not aavs_fragiles:
        raise HTTPException(status_code=404, detail="Aucun AAV fragile détecté.")
    return aavs_fragiles

@router.get("/students-at-risk", response_model=List[ApprenantRisque])
def get_students_at_risk(id_ontologie: int) -> List[ApprenantRisque]:
    """Récupère les apprenants en difficulté."""
    apprenants_risque = detecter_apprenants_risque(id_ontologie)
    if not apprenants_risque:
        raise HTTPException(status_code=404, detail=f"Aucun apprenant à risque trouvé pour l'ontologie {id_ontologie}.")
    return apprenants_risque