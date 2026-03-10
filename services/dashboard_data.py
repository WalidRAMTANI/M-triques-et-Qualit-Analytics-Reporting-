from database import get_db_connection
from typing import Optional
from database import from_json

def get_teacher_stats(teacher_id: str, discipline: str)-> Optional[dict]:
    """
    Calculates overall teacher performance for a specific discipline.
    Joins AAVs with metrics and counts unique students via attempts.
    """
    with get_db_connection() as coon:
        cursor = coon.cursor()
        cursor.execute(""" SELECT COALESCE(AVG(metr.taux_succes_moyen), 0) AS moyenne , count(DISTINCT aav.id_aav) AS nb_aav, count(DISTINCT tent.id_apprenant) AS nb_apprenants
                        from enseignant as ens left join aav on aav.id_enseignant = ens.id_enseignant left join metrique_qualite_aav as metr on metr.id_aav = aav.id_aav left join tentative as tent on tent.id_aav_cible = aav.id_aav
                        where ens.id_enseignant = ? and aav.discipline = ?
                        """, (teacher_id, discipline))
        res = cursor.fetchone() 
        return dict(res)
        
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
        cursor.execute(f""" select count(id_aav) as nb_aav, AVG(score_covering_ressources) as moyenne_covering from metrique_qualite_aav where id_aav IN ({char}) """, res_ids)
        res = cursor.fetchone()
        return dict(res)