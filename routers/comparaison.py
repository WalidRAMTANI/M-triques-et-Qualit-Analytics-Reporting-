from fastapi import APIRouter, Query, HTTPException
from schemas import AAVComparaison, ApprenantComparaison
from services.report_generator import collect_data_for_aav, collect_data_for_student
from typing import List
from services.alert_detector import get_apprenants_ontologie, calculer_progression, count_aavs_bloques
router = APIRouter()

@router.get("/aavs", response_model=List[AAVComparaison])
def compare_aavs(ids: str = Query(..., description="IDs separated by commas, ex: 1,2,3")) -> List[AAVComparaison]:
    """ a function that compare multiple AAVs """
    aav_list = []
    # Test all IDs and fetch the data safely, ignoring Nones
    for id in ids.split(","):
        # We enforce "json" format since comparisons only return generic JSON metric schemas
        data = collect_data_for_aav(int(id.strip()), "json") 
        if data:
            aav_list.append(data)
            
    if not aav_list:
        raise HTTPException(status_code=404, detail=f"Aucun AAV trouvé pour les identifiants fournis: {ids}")
    
    return aav_list

@router.get("/learners", response_model=List[ApprenantComparaison])
def compare_learners(id_ontologie: int = Query(..., description="ID of the ontology")) -> List[ApprenantComparaison]:
    """ a function that compare multiple Learners """
    apprenants = get_apprenants_ontologie(id_ontologie)
    if not apprenants:
        raise HTTPException(status_code=404, detail=f"Aucun apprenant trouvé pour l'ontologie {id_ontologie}")
        
    result = []
    for apprenant in apprenants:
        # Enforce json format to retrieve dictionary metrics
        student_data = collect_data_for_student(apprenant["id_apprenant"], "json")
        nb_tentatives = student_data["nb_tentatives"] if student_data else 0
        
        result.append(ApprenantComparaison(
            id_apprenant=apprenant["id_apprenant"], 
            nom=apprenant["nom_utilisateur"], 
            progression=calculer_progression(apprenant["id_apprenant"]), 
            aavs_bloques=count_aavs_bloques(apprenant["id_apprenant"]),
            nb_tentatives=nb_tentatives,
        ))
        
    return result