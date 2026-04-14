import fastapi
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.services.alert_detector import detecter_aavs_difficiles, detecter_aavs_inutilises, detecter_aavs_fragiles, detecter_apprenants_risque
from app.model.schemas import AAVDifficile, AAVInutilise, AAVFragile, ApprenantRisque

router = APIRouter()

# GET /alerts/difficult-aavs  - AAV avec taux de succès anormalement bas
# GET /alerts/unused-aavs     - AAV jamais ou rarement utilisés
# GET /alerts/fragile-aavs    - AAV avec forte variance dans les résultats
# GET /alerts/students-at-risk - Apprenants en difficulté

@router.get("/difficult-aavs", response_model=List[AAVDifficile])
def get_difficult_aavs() -> List[AAVDifficile]:
    """
    Récupère la liste des AAV ayant un taux de succès anormalement bas.

    Returns:
        List[AAVDifficile]: Liste des AAV difficiles détectés.

    Raises:
        HTTPException: 404 si aucun AAV difficile n'est trouvé.
    """
    
    aavs_difficiles = detecter_aavs_difficiles()
    if not aavs_difficiles:
        raise HTTPException(status_code=404, detail="Aucun AAV difficile détecté.")
    return aavs_difficiles
    
@router.get("/unused-aavs", response_model=List[AAVInutilise])
def get_unused_aavs() -> List[AAVInutilise]:
    """
    Récupère la liste des AAV qui n'ont jamais été utilisés dans un exercice.

    Returns:
        List[AAVInutilise]: Liste des AAV inutilisés.

    Raises:
        HTTPException: 404 si aucun AAV inutilisé n'est trouvé.
    """
    aavs_inutilises = detecter_aavs_inutilises()
    if not aavs_inutilises:
        raise HTTPException(status_code=404, detail="Aucun AAV inutilisé détecté.")
    return aavs_inutilises

@router.get("/fragile-aavs", response_model=List[AAVFragile])
def get_fragile_aavs() -> List[AAVFragile]:
    """
    Récupère la liste des AAV présentant une forte variance dans les résultats des élèves.

    Returns:
        List[AAVFragile]: Liste des AAV fragiles.

    Raises:
        HTTPException: 404 si aucun AAV fragile n'est trouvé.
    """
    aavs_fragiles = detecter_aavs_fragiles()
    if not aavs_fragiles:
        raise HTTPException(status_code=404, detail="Aucun AAV fragile détecté.")
    return aavs_fragiles

@router.get("/students-at-risk/{id_ontologie}", response_model=List[ApprenantRisque])
def get_students_at_risk(id_ontologie: int) -> List[ApprenantRisque]:
    """
    Récupère la liste des apprenants en difficulté pour une ontologie donnée.

    Args:
        id_ontologie (int): L'identifiant de l'ontologie cible.

    Returns:
        List[ApprenantRisque]: Liste des apprenants à risque.

    Raises:
        HTTPException: 404 si aucun apprenant à risque n'est trouvé.
    """
    apprenants_risque = detecter_apprenants_risque(id_ontologie)
    if not apprenants_risque:
        raise HTTPException(status_code=404, detail=f"Aucun apprenant à risque trouvé pour l'ontologie {id_ontologie}.")
    return apprenants_risque