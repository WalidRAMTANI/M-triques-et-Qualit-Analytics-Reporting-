from fastapi import APIRouter
from schemas import RapportResponse, RapportRequest, RapportGlobalResponse
from services.report_generator import generer_rapport_personnalise, generer_rapport_global
from model import Rapport
router = APIRouter()

@router.post("/generate", response_model=Rapport, status_code=201)
def generate_rapport_personnalise(request: RapportRequest) -> Rapport:
    """Génère un rapport personnalisé (par AAV, apprenant ou discipline)."""
    return generer_rapport_personnalise(
        type=request.type,
        id_cible=request.id_cible,
        debut=request.date_debut,
        fin=request.date_fin,
        format=request.format
    )

@router.get("/global", response_model=RapportGlobalResponse)
def get_rapport_global() -> RapportGlobalResponse:
    """Rapport global de l'ontologie : métriques de tous les AAV + alertes."""
    return generer_rapport_global()

