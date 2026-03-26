from fastapi import APIRouter, HTTPException
from app.model.model import MetriqueQualiteAAV
from app.services import metric_calculator
from app.services.metric_calculator import calculer_metriques_aav, get_aav, get_metriques_by_aav, get_all_metrics, get_history
from typing import Optional

router = APIRouter()

# IMPORTANT: Place catch-all routes LAST to avoid matching issues
# Routes with fixed paths (e.g., /history, /calculate) must come before /{id_aav}

@router.get("/", response_model=list[MetriqueQualiteAAV])
def get_all_metrics_route(score_covering_ressources: Optional[float]=None, taux_succes_moyen: Optional[float]=None, est_utilisable: Optional[bool]=None, nb_tentatives_total: Optional[int]=None, nb_apprenants_distincts: Optional[int]=None, ecart_type_scores: Optional[float]=None):
    """Retrieve all latest quality metrics for all AAVs."""
    filtres = {
        "score_covering_ressources": score_covering_ressources,
        "taux_succes_moyen": taux_succes_moyen,
        "nb_tentatives_total": nb_tentatives_total,
        "nb_apprenants_distincts": nb_apprenants_distincts,
        "ecart_type_scores": ecart_type_scores
    }
    metrics = get_all_metrics(filtres)
    if not metrics:
        raise HTTPException(status_code=404, detail="Aucune métrique trouvée")
    return metrics

@router.post("/{id_aav}/calculate", response_model=MetriqueQualiteAAV)
def calculate_metric(id_aav: int):
    """Asynchronously triggers the quality metrics calculation for a specific AAV by ID."""
    if not get_aav(id_aav):
        raise HTTPException(status_code=404, detail=f"Impossible de calculer les métriques pour l'AAV {id_aav} (AAV introuvable ?)")
    metric = calculer_metriques_aav(id_aav)
    if not metric:
        raise HTTPException(status_code=404, detail=f"Impossible de calculer les métriques pour l'AAV {id_aav} (AAV introuvable ?)")
    return metric

@router.get("/{id_aav}/history", response_model = list[MetriqueQualiteAAV])
def get_history_metrics(id_aav :int):
    """Retrieves the history of metrics calculations for a specific AAV."""
    if not get_aav(id_aav):
        raise HTTPException(status_code=404, detail=f"Aucune AAV trouvée pour l'ID {id_aav}")
    history = get_history(id_aav)
    return history

@router.get("/{id_aav}", response_model=MetriqueQualiteAAV)
def metrique_qualite_aav(id_aav: int):
    """Retrieves the quality metrics for a specific AAV by ID."""
    if not get_aav(id_aav):
        raise HTTPException(status_code=404, detail=f"Aucune AAV trouvée pour l'ID {id_aav}")
    metriques = get_metriques_by_aav(id_aav)
    if not metriques:
        raise HTTPException(status_code=404, detail=f"Aucune métrique trouvée pour l'AAV {id_aav}")
    return metriques