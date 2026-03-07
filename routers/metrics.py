from fastapi import APIRouter
from model import MetriqueQualiteAAV
from services import metric_calculator
from services.metric_calculator import calculer_metriques_aav, get_aav, get_metriques_by_aav, get_all_metrics,get_history_metrics

router = APIRouter()

@router.get("/{id_aav}", response_model=MetriqueQualiteAAV)
def metrique_qualite_aav(id_aav: int):
    return  get_metriques_by_aav(id_aav)

@router.get("/", response_model=list[MetriqueQualiteAAV])
def get_all_metrics():
    return get_all_metrics()

@router.post("/{id_aav}/calculate", response_model=MetriqueQualiteAAV)
def calculate_metric(id_aav: int):
    return calculer_metriques_aav(id_aav) 

@router.get("/{id_aav}/history", response_model = list[MetriqueQualiteAAV])
def get_history_metrics(id_aav :int):
    return get_history_metrics(id_aav)