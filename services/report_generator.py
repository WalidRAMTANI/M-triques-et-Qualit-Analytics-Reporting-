
import json
from datetime import datetime
from database import get_db_connection
from services.metric_calculator import get_all_aavs, get_aav,calculer_couverture, calculer_taux_succes,determiner_utilisabilite, count_attempts, count_distinct_learners
from database import to_json, RapportRepository
from services.alert_detector import detecter_aavs_difficiles, detecter_aavs_fragiles,detecter_aavs_inutilises

from model import Rapport, LearnerBase
from schemas import AAVComparaison, ApprenantComparaison, RapportGlobalResponse

def get_student(student_id: int) -> LearnerBase:
    """Récupère un apprenant par son ID. Retourne None si introuvable."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM apprenant WHERE id_apprenant = ?", (student_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id_apprenant": row["id_apprenant"],
                "nom": row["nom_utilisateur"],
                "email": row["email"],
                "date_inscription": row["date_inscription"],
                "derniere_connexion": row["derniere_connexion"]
            }
        return None

def collect_data_for_aav(id_aav: int) -> AAVComparaison:
    """
    Collecte toutes les données nécessaires pour un AAV donné.
    """
    aav = get_aav(id_aav)
    if not aav:

        return None
    return {"id_aav": aav["id_aav"],
        "nom": aav["nom"],
        "taux_succes": calculer_taux_succes(id_aav),
        "couverture": calculer_couverture(id_aav),
        "utilisabilite": determiner_utilisabilite(id_aav),
        "nb_tentatives": count_attempts(id_aav),
        "nb_apprenants": count_distinct_learners(id_aav)
    }
    
def collect_data_for_student(id_cible: int) -> dict:
    """
    Collecte toutes les données nécessaires pour un apprenant donné.
    """
    student = get_student(id_cible)
    if not student:

        return None
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.id_aav_cible as id_aav, a.nom, t.score_obtenu, t.date_tentative
            FROM tentative t
            JOIN aav a ON t.id_aav_cible = a.id_aav
            WHERE t.id_apprenant = ?
            ORDER BY t.date_tentative DESC
        """, (id_cible,))
        tentatives = [dict(row) for row in cursor.fetchall()]
    return {
        "id_apprenant": student["id_apprenant"] if isinstance(student, dict) else student.id_apprenant,
        "nom": student["nom"] if isinstance(student, dict) else student.nom,
        "nb_tentatives": len(tentatives),
        "tentatives": tentatives,
    }
    

def collect_data_for_discipline(id_cible: str) -> dict:
    """
    Collecte toutes les données nécessaires pour une discipline donnée.
    """
    aavs = [aav for aav in get_all_aavs() if aav["discipline"] == id_cible]
    aav_ids = {aav["id_aav"] for aav in aavs}  # set des IDs de la discipline

    results = []
    for aav in aavs:
        results.append({
            "id_aav": aav["id_aav"],
            "nom": aav["nom"],
            "taux_succes": calculer_taux_succes(aav["id_aav"]),
            "couverture": calculer_couverture(aav["id_aav"]),
            "utilisabilite": determiner_utilisabilite(aav["id_aav"])
        })
    return {
        "discipline": id_cible,
        "aavs": results,
        "nb_aavs": len(results),
        "alertes": {
            "difficiles": [a for a in detecter_aavs_difficiles() if a["id_aav"] in aav_ids],
            "fragiles":   [a for a in detecter_aavs_fragiles()   if a["id_aav"] in aav_ids],
            "inutilises": [a for a in detecter_aavs_inutilises() if a["id_aav"] in aav_ids]
        }
    }

def generer_rapport_personnalise(type, id_cible, debut, fin, format):
    """
    Generate a personalized report based on the type of report, id_cible, date_debut, date_fin and format.
    """
    if type == "aav":
        data = collect_data_for_aav(int(id_cible))
    elif type == "student":
        data = collect_data_for_student(int(id_cible))
    elif type == "discipline":
        data = collect_data_for_discipline(id_cible)
    else:
        raise ValueError(f"Type de rapport inconnu : {type}")

    rapport = Rapport(
        type_rapport=type,
        id_cible=id_cible,
        periode_debut=debut,
        periode_fin=fin,
        format=format,
        date_generation=datetime.now(),
        contenu=to_json(data),
        format_fichier=format
    )
    return RapportRepository().create(rapport)


def generer_rapport_global() -> RapportGlobalResponse:
    """Generate a global report of the ontology: metrics of all AAVs + alerts."""
    aavs = get_all_aavs()

    aavs_data = [
        {
            "id_aav": aav["id_aav"],
            "nom": aav["nom"],
            "taux_succes": calculer_taux_succes(aav["id_aav"]),
            "couverture": calculer_couverture(aav["id_aav"]),
            "utilisabilite": determiner_utilisabilite(aav["id_aav"]),
            "nb_tentatives": count_attempts(aav["id_aav"]),
        }
        for aav in aavs
    ]

    nb_utilisables = sum(1 for a in aavs_data if a["utilisabilite"])

    difficiles  = detecter_aavs_difficiles()
    fragiles    = detecter_aavs_fragiles()
    inutilises  = detecter_aavs_inutilises()

    return RapportGlobalResponse(
        date_generation=datetime.now().isoformat(),
        nb_aavs_total=len(aavs),
        nb_aavs_utilisables=nb_utilisables,
        nb_alertes= {
            "difficiles": len(difficiles),
            "fragiles":   len(fragiles),
            "inutilises": len(inutilises),
        },
        alertes= {
            "difficiles": [a.model_dump() for a in difficiles],
            "fragiles":   [a.model_dump() for a in fragiles],
            "inutilises": [a.model_dump() for a in inutilises],
        },
        aavs= aavs_data,
    )
