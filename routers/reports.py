from fastapi import APIRouter, HTTPException
from datetime import datetime
from schemas import RapportResponse, RapportRequest, RapportGlobalResponse
from services.report_generator import generer_rapport_personnalise, generer_rapport_global
from model import Rapport
router = APIRouter()

@router.post("/generate", response_model=Rapport, status_code=201)
def generate_rapport_personnalise(request: RapportRequest) -> Rapport:
    """Génère un rapport personnalisé (par AAV, apprenant ou discipline)."""
    rapport = generer_rapport_personnalise(
        type=request.type,
        id_cible=request.id_cible,
        debut=request.date_debut,
        fin=request.date_fin,
        format=request.format
    )
    if not rapport:
        raise HTTPException(status_code=404, detail=f"Aucune donnée trouvée pour la cible {request.id_cible} (Type: {request.type})")
        
    return rapport

@router.get("/global", response_model=RapportGlobalResponse)
def get_rapport_global() -> RapportGlobalResponse:
    """Rapport global de l'ontologie : métriques de tous les AAV + alertes."""
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

