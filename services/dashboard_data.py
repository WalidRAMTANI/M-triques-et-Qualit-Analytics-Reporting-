from database import get_db_connection
from typing import Optional
from database import from_json

def get_teacher_stats(teacher_id: int)-> Optional[dict]:
    """Calculates the overall performance of a teacher's students. It first identifies the subjects taught,
       then computes the average success rate and the total number of students involved"""
    with get_db_connection() as coon:
        cursor = coon.cursor()
        cursor.execute(""" SELECT discipline from enseignant where id_enseignant = ? """, (teacher_id,))
        row = cursor.fetchone()
        if not row:
            return None
        res_discipline = from_json(row[0])
        char = ""
        for elem in range(len(res_discipline)):
            char += "?"
            if elem < len(res_discipline) - 1:
                char += ","
        cursor.execute(f""" SELECT COALESCE(avg(metr.taux_succes_moyen), 0) AS moyenne, count(distinct(aav.id_aav)) AS nb_aav, count(distinct(tent.id_apprenant)) AS nb_apprenants from aav left join metrique_qualite_aav metr on aav.id_aav = metr.id_aav 
                       left join tentative tent on tent.id_aav_cible = aav.id_aav where aav.discipline IN ({char}) AND aav.is_active = 1 """,res_discipline)
        res = cursor.fetchone() 
        result = dict(res)
        result["disciplines"] = res_discipline
        return result
def get_discipline_stats( discipline_name: str)-> Optional[dict]:
    """
    Global discipline analysis: average success and resource coverage rate.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(""" SELECT COALESCE(AVG(taux_succes_moyen), 0) AS moyenne, 
                        AVG(score_covering_ressources) AS moyenne_covering, COUNT(aav.id_aav) AS nb 
                        from metrique_qualite_aav join aav on metrique_qualite_aav.id_aav = aav.id_aav WHERE discipline = ? """, (discipline_name,))
        res = cursor.fetchone()
        return dict(res) 
    
def get_ontology_cov( id_reference: int)-> Optional[dict]:
    """
    Analyzes coverage for a specific ontology (curriculum).
    Retrieves the list of active AAV IDs from the ontology JSON.
    Calculates the average coverage score for these specific IDs.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(""" SELECT aavs_ids_actifs FROM ontology_reference WHERE id_reference = ? """, (id_reference,))
        row = cursor.fetchone()
        if not row:
            return None
        res_ids = from_json(row[0])  
        char = ""
        for elem in range(len(res_ids)):
            char += "?"
            if elem < len(res_ids) - 1:
                char += ","
        cursor.execute(f""" select count(id_aav) as nb_aav, COALESCE(AVG(score_covering_ressources)) as moyenne_covering from metrique_qualite_aav where id_aav IN ({char}) """, res_ids)
        res = cursor.fetchone()
        return dict(res)