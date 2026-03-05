from fastapi import APIRouter, Query
from schemas import AAVComparaison, ApprenantComparaison
from services.report_generator import collect_data_for_aav, collect_data_for_student
from typing import List
from services.alert_detector import get_apprenants_ontologie, calculer_progression, count_aavs_bloques
router = APIRouter()

@router.get("/aavs", response_model=List[AAVComparaison])
def compare_aavs(ids: str = Query(..., description="IDs separated by commas, ex: 1,2,3")) -> List[AAVComparaison]:
    """ a function that compare multiple AAVs """
    return [collect_data_for_aav(int(id)) for id in ids.split(",")]

@router.get("/learners", response_model=List[ApprenantComparaison])
def compare_learners(id_ontologie: int = Query(..., description="ID of the ontology")) -> List[ApprenantComparaison]:
    """ a function that compare multiple Learners """
    return [ApprenantComparaison(
        id_apprenant=apprenant["id_apprenant"], 
        nom=apprenant["nom_utilisateur"], 
        progression=calculer_progression(apprenant["id_apprenant"]), 
        aavs_bloques=count_aavs_bloques(apprenant["id_apprenant"]),
        nb_tentatives=collect_data_for_student(apprenant["id_apprenant"])["nb_tentatives"],
    ) for apprenant in get_apprenants_ontologie(id_ontologie)]