from database import get_db_session, EnseignantModel, AAVModel, MetriqueQualiteAAVModel, TentativeModel, OntologyReferenceModel
from typing import Optional
from sqlalchemy import func

def get_enseignant(id_enseignant: int):
    with get_db_session() as db:
        return db.get(EnseignantModel, id_enseignant)

def get_teacher_stats(teacher_id: int) -> Optional[dict]:
    """Calculates the overall performance of a teacher's students."""
    with get_db_session() as db:
        enseignant = db.get(EnseignantModel, teacher_id)
        if not enseignant:
            return None
        
        disciplines = enseignant["discipline"]
        if not disciplines:
            return {"moyenne": 0, "nb_aav": 0, "nb_apprenants": 0, "disciplines": []}

        res = db.query(
            func.coalesce(func.avg(MetriqueQualiteAAVModel.taux_succes_moyen), 0).label("moyenne"),
            func.count(func.distinct(AAVModel.id_aav)).label("nb_aav"),
            func.count(func.distinct(TentativeModel.id_apprenant)).label("nb_apprenants")
        ).select_from(AAVModel).join(
            MetriqueQualiteAAVModel, AAVModel.id_aav == MetriqueQualiteAAVModel.id_aav, isouter=True
        ).join(
            TentativeModel, TentativeModel.id_aav_cible == AAVModel.id_aav, isouter=True
        ).filter(
            AAVModel.discipline.in_(disciplines),
            AAVModel.is_active == True
        ).first()

        return {
            "moyenne": float(res.moyenne),
            "nb_aav": res.nb_aav,
            "nb_apprenants": res.nb_apprenants,
            "disciplines": disciplines
        }

def get_discipline_stats(discipline_name: str):
    with get_db_session() as db:
        res = db.query(
            func.coalesce(func.avg(MetriqueQualiteAAVModel.taux_succes_moyen), 0).label("moyenne"),
            func.coalesce(func.avg(MetriqueQualiteAAVModel.score_covering_ressources), 0).label("moyenne_covering"),
            func.count(AAVModel.id_aav).label("nb")
        ).join(
            AAVModel, MetriqueQualiteAAVModel.id_aav == AAVModel.id_aav
        ).filter(
            AAVModel.discipline == discipline_name
        ).first()
        
        return {
            "moyenne": float(res.moyenne),
            "moyenne_covering": float(res.moyenne_covering),
            "nb": res.nb
        }

def get_ontology_cov(id_reference: int) -> Optional[dict]:
    with get_db_session() as db:
        onto = db.get(OntologyReferenceModel, id_reference)
        if not onto or not onto["aavs_ids_actifs"]:
            return None
        
        res_ids = onto["aavs_ids_actifs"]
        res = db.query(
            func.count(MetriqueQualiteAAVModel.id_aav).label("nb_aav"),
            func.coalesce(func.avg(MetriqueQualiteAAVModel.score_covering_ressources), 0).label("moyenne_covering")
        ).filter(
            MetriqueQualiteAAVModel.id_aav.in_(res_ids)
        ).first()
        
        return {
            "nb_aav": res.nb_aav,
            "moyenne_covering": float(res.moyenne_covering)
        }