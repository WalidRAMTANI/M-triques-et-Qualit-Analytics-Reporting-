from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.model.schemas import RapportResponse, RapportRequest, RapportGlobalResponse
from app.services.report_generator import generer_rapport_personnalise, generer_rapport_global
from app.model.model import Rapport
router = APIRouter()

@router.post("/generate", response_model=Rapport, status_code=201)
def generate_rapport_personnalise(request: RapportRequest) -> Rapport:
    """
    Génère un rapport personnalisé filtré par type (AAV, Apprenant, Discipline).

    Args:
        request (RapportRequest): Paramètres du rapport (type, id_cible, période, format).

    Returns:
        Rapport: Le rapport généré.

    Raises:
        HTTPException: 404 si aucune donnée n'est trouvée pour la cible demandée.
    """
    rapport = generer_rapport_personnalise(
        type=request.type_rapport,
        id_cible=request.id_cible,
        debut=request.periode_debut,
        fin=request.periode_fin,
        format=request.format
    )
    if not rapport:
        raise HTTPException(status_code=404, detail=f"Aucune donnée trouvée pour la cible {request.id_cible} (Type: {request.type_rapport})")
        
    return rapport

@router.get("/global", response_model=RapportGlobalResponse)
def get_rapport_global() -> RapportGlobalResponse:
    """
    Récupère un rapport global sur l'ensemble de l'ontologie.
    Inclut des métriques agrégées sur tous les AAVs et les alertes en cours.

    Returns:
        RapportGlobalResponse: Le rapport global contenant les statistiques et alertes.
    """
    rapport = generer_rapport_global()
    if rapport:
        return rapport
    return RapportGlobalResponse(
        date_generation="",
        nb_aavs_total=0,
        nb_aavs_utilisables=0,
        nb_alertes={},
        alertes={},
        aavs=[]
    )

