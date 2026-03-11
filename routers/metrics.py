from fastapi import APIRouter, HTTPException
from model import MetriqueQualiteAAV
from services import metric_calculator
from services.metric_calculator import calculer_metriques_aav, get_aav, get_metriques_by_aav, get_all_metrics, get_history

router = APIRouter()

@router.get("/{id_aav}", response_model=MetriqueQualiteAAV)
def metrique_qualite_aav(id_aav: int):
    
    metriques = get_metriques_by_aav(id_aav)
    if not metriques:
        raise HTTPException(status_code=404, detail=f"Aucune métrique trouvée pour l'AAV {id_aav}")
    return metriques

@router.get("/", response_model=list[MetriqueQualiteAAV])
def get_all_metrics_route():
    metrics = get_all_metrics()
    if not metrics:
        raise HTTPException(status_code=404, detail="Aucune métrique trouvée")
    return metrics

@router.post("/{id_aav}/calculate", response_model=MetriqueQualiteAAV)
def calculate_metric(id_aav: int):
    metric = calculer_metriques_aav(id_aav)
    if not metric:
        raise HTTPException(status_code=404, detail=f"Impossible de calculer les métriques pour l'AAV {id_aav} (AAV introuvable ?)")
    return metric

@router.get("/{id_aav}/history", response_model = list[MetriqueQualiteAAV])
def get_history_metrics(id_aav :int):
    history = get_history(id_aav)
    if not history:
        raise HTTPException(status_code=404, detail=f"Aucun historique trouvé pour l'AAV {id_aav}")
    return history