from database import get_db_connection
from typing import Optional

def get_teacher_stats(self, teacher_id: str)-> Optional[dict]:
    with get_db_connection() as coon:
        cursor = coon.cursor()
        cursor.execute(""" SELECT AVG(taux_succes_moyen) AS moyenne FROM metrique_qualite_aav join aav
                         on metrique_qualite_aav.id_aav = aav.id_aav WHERE enseignement = ?
                           
                        """, (teacher_id,))
        res = cursor.fetchone() 
        return dict(res)
        
def get_discipline_stats(self, discipline_name: str)-> Optional[dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(""" SELECT AVG(taux_succes_moyen) AS moyenne, 
                        AVG(score_covering_ressources) AS moyenne_covering, COUNT(id_aav) AS nb 
                        from metrique_qualite_aav join aav on metrique_qualite_aav.id_aav = aav.id_aav WHERE discipline = ? """, (discipline_name,))
        res = cursor.fetchone()
        return dict(res) 