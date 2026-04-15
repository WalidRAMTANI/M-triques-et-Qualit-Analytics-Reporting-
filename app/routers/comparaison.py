from fastapi import APIRouter, Query, HTTPException
from app.model.schemas import AAVComparaison, ApprenantComparaison
from app.services.report_generator import collect_data_for_aav, collect_data_for_student
from typing import List
from app.services.alert_detector import get_apprenants_ontologie, calculer_progression, count_aavs_bloques
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
    from app.database import get_db_connection, StatutApprentissageModel
    
    with get_db_connection() as session:
        for apprenant in apprenants:
            learner_id = apprenant["id_apprenant"]
            
            # Count AAVs statuses
            maitrise = session.query(StatutApprentissageModel).filter(
                StatutApprentissageModel.id_apprenant == learner_id,
                StatutApprentissageModel.niveau_maitrise >= 1.0
            ).count()
            
            encours = session.query(StatutApprentissageModel).filter(
                StatutApprentissageModel.id_apprenant == learner_id,
                StatutApprentissageModel.niveau_maitrise < 1.0,
                StatutApprentissageModel.niveau_maitrise > 0.0
            ).count()
            
            result.append(ApprenantComparaison(
                id_apprenant=learner_id, 
                nom_utilisateur=apprenant["nom_utilisateur"], 
                progression_globale=calculer_progression(learner_id), 
                aavs_maitrise=maitrise,
                aavs_encours=encours
            ))
        
    return result