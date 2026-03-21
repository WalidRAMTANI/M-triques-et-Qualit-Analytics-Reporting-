import base64
from typing import List, Optional, Any
from datetime import datetime
from app.database import get_db_connection, to_json, RapportRepository
from app.services.metric_calculator import get_all_aavs, get_aav, calculer_couverture, calculer_taux_succes, determiner_utilisabilite, count_attempts, count_distinct_learners
from app.services.alert_detector import detecter_aavs_difficiles, detecter_aavs_fragiles, detecter_aavs_inutilises
from app.model.model import Rapport, LearnerBase
from app.model.schemas import AAVComparaison, ApprenantComparaison, RapportGlobalResponse

# helper for pdf
def to_pdf(data_dict, title="Rapport"):
    text = f"{title}\n\n"
    
    def format_dict(d, indent=0):
        res = ""
        prefix = " " * indent
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, (dict, list)):
                    res += f"{prefix}{k}:\n"
                    res += format_dict(v, indent + 4)
                else:
                    res += f"{prefix}{k}: {v}\n"
        elif isinstance(d, list):
            for item in d:
                if isinstance(item, (dict, list)):
                    res += f"{prefix}-\n"
                    res += format_dict(item, indent + 4)
                else:
                    res += f"{prefix}- {item}\n"
        return res
    
    text += format_dict(data_dict)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
    lines = text.split('\n')
    
    stream = "BT\n/F1 12 Tf\n50 800 Td\n15 TL\n"
    for line in lines[:50]:
        stream += f"({line}) Tj T*\n"
    stream += "ET"
    
    obj1 = "<</Type /Catalog /Pages 2 0 R>>"
    obj2 = "<</Type /Pages /Kids [3 0 R] /Count 1>>"
    obj3 = "<</Type /Page /Parent 2 0 R /Resources <</Font <</F1 4 0 R>>>> /MediaBox [0 0 595 842] /Contents 5 0 R>>"
    obj4 = "<</Type /Font /Subtype /Type1 /BaseFont /Helvetica>>"
    obj5 = f"<</Length {len(stream)}>>\nstream\n{stream}\nendstream"
    
    objects = [obj1, obj2, obj3, obj4, obj5]
    pdf_content = b"%PDF-1.4\n"
    offsets = []
    
    for i, obj in enumerate(objects):
        offsets.append(len(pdf_content))
        pdf_content += f"{i+1} 0 obj\n{obj}\nendobj\n".encode('ascii')
        
    xref_pos = len(pdf_content)
    pdf_content += b"xref\n0 6\n0000000000 65535 f \n"
    for offset in offsets:
        pdf_content += f"{offset:010d} 00000 n \n".encode('ascii')
        
    pdf_content += f"trailer\n<</Size 6 /Root 1 0 R>>\nstartxref\n{xref_pos}\n%%EOF\n".encode('ascii')
    return base64.b64encode(pdf_content).decode('ascii')


def generate_csv_string(data, field):
    import csv, io
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=field)
    writer.writeheader()
    
    if isinstance(data, dict):
        data = [data]
    elif isinstance(data, list) and len(data) > 0 and not isinstance(data[0], dict):
        if len(data) == len(field):
            data = [dict(zip(field, data))]
    
    writer.writerows(data)
    return output.getvalue()

def get_student(student_id: int) -> Optional[dict]:
    """
    Retrieve learner information by ID.
    
    Fetches complete learner details including name, email, registration date,
    and last connection date.
    
    Args:
        student_id (int): The ID of the learner to retrieve.
    
    Returns:
        Optional[dict]: Learner dictionary or None if not found.
    
    Example:
        >>> get_student(1)
        {'id_apprenant': 1, 'nom': 'Alice', 'email': 'alice@example.com', ...}
    """
    with get_db_connection() as session:
        from database import ApprenantModel
        # Query learner by ID
        apprenant = session.query(ApprenantModel).filter(
            ApprenantModel.id_apprenant == student_id
        ).first()
        if apprenant:
            return {
                "id_apprenant":      apprenant.id_apprenant,
                "nom":               apprenant.nom_utilisateur,
                "email":             apprenant.email,
                "date_inscription":  apprenant.date_inscription,
                "derniere_connexion": apprenant.derniere_connexion
            }
        return None

def collect_data_for_aav(id_aav: int, format: str) -> any:
    aav = get_aav(id_aav)
    if not aav:
        return None
    
    data_dict = {
        "id_aav": aav["id_aav"], 
        "nom": aav["nom"], 
        "taux_succes": calculer_taux_succes(id_aav), 
        "couverture": calculer_couverture(id_aav), 
        "utilisabilite": determiner_utilisabilite(id_aav), 
        "nb_tentatives": count_attempts(id_aav), 
        "nb_apprenants": count_distinct_learners(id_aav)
    }

    if format == "csv":
        return generate_csv_string(data_dict, ["id_aav", "nom", "taux_succes", "couverture", "utilisabilite", "nb_tentatives", "nb_apprenants"])
    elif format == "pdf":
        return to_pdf(data_dict, title=f"Rapport AAV - {aav['nom']}")
    elif format == "json":
        return data_dict
    else:
        raise ValueError(f"Format de rapport inconnu : {format}")
    
from sqlalchemy import func

def collect_data_for_student(id_cible: int, format: str) -> dict:
    """
    Collect all learning data for a specific learner.
    
    Gathers all attempts made by the learner, with associated AAV information,
    sorted by date in descending order. Returns data in the requested format
    (CSV, PDF, or JSON).
    
    Args:
        id_cible (int): The ID of the learner to generate report for.
        format (str): Output format - 'csv', 'pdf', or 'json'.
    
    Returns:
        dict: Formatted report data, or None if learner not found.
    
    Example:
        >>> collect_data_for_student(1, 'json')
        {'id_apprenant': 1, 'nom': 'Alice', 'tentatives': [...]}
    """
    student = get_student(id_cible)
    if not student:
        return None

    with get_db_connection() as session:
        from database import TentativeModel, AAVModel
        # Get all attempts for this learner, ordered by date
        tentatives = session.query(
            TentativeModel.id_aav_cible.label("id_aav"),
            AAVModel.nom,
            TentativeModel.score_obtenu,
            TentativeModel.date_tentative
        ).join(AAVModel, TentativeModel.id_aav_cible == AAVModel.id_aav)\
         .filter(TentativeModel.id_apprenant == id_cible)\
         .order_by(TentativeModel.date_tentative.desc()).all()

        tentatives_list = [
            {
                "id_aav": t.id_aav,
                "nom": t.nom,
                "score_obtenu": t.score_obtenu,
                "date_tentative": t.date_tentative,
            }
            for t in tentatives
        ]

    id_apprenant = student["id_apprenant"]
    nom_apprenant = student["nom"]

    if format == "csv":
        flat_data = [
            {
                "id_apprenant":  id_apprenant,
                "nom_apprenant": nom_apprenant,
                "id_aav":        t.get("id_aav"),
                "nom_aav":       t.get("nom"),
                "score_obtenu":  t.get("score_obtenu"),
                "date_tentative": t.get("date_tentative"),
            }
            for t in tentatives_list
        ]
        return generate_csv_string(
            flat_data,
            ["id_apprenant", "nom_apprenant", "id_aav", "nom_aav", "score_obtenu", "date_tentative"]
        )

    elif format == "pdf":
        return to_pdf(tentatives_list, title=f"Rapport Apprenant - {nom_apprenant} ({id_apprenant})")

    elif format == "json":
        return {
            "id_apprenant":  id_apprenant,
            "nom":           nom_apprenant,
            "nb_tentatives": len(tentatives_list),
            "tentatives":    tentatives_list,
        }

    else:
        raise ValueError(f"Format de rapport inconnu : {format}")
        
def collect_data_for_discipline(id_cible: str,format: str) -> dict:
    """
    Collects all necessary data for a given discipline.
    """
    aavs = [aav for aav in get_all_aavs() if aav["discipline"] == id_cible]
    aav_ids = {aav["id_aav"] for aav in aavs}

    results = []
    for aav in aavs:
        results.append({
            "id_aav": aav["id_aav"],
            "nom": aav["nom"],
            "taux_succes": calculer_taux_succes(aav["id_aav"]),
            "couverture": calculer_couverture(aav["id_aav"]),
            "utilisabilite": determiner_utilisabilite(aav["id_aav"])
        })

    if format == "csv":
        difficiles_ids = {a.id_aav for a in detecter_aavs_difficiles() if a.id_aav in aav_ids}
        fragiles_ids = {a.id_aav for a in detecter_aavs_fragiles() if a.id_aav in aav_ids}
        inutilises_ids = {a.id_aav for a in detecter_aavs_inutilises() if a.id_aav in aav_ids}
        
        flat_data = []
        for aav_data in results:
            flat_data.append({
                "discipline": id_cible,
                "id_aav": aav_data["id_aav"],
                "nom": aav_data["nom"],
                "taux_succes": aav_data["taux_succes"],
                "couverture": aav_data["couverture"],
                "utilisabilite": aav_data["utilisabilite"],
                "alerte_difficile": aav_data["id_aav"] in difficiles_ids,
                "alerte_fragile": aav_data["id_aav"] in fragiles_ids,
                "alerte_inutilise": aav_data["id_aav"] in inutilises_ids
            })
        
        columns = ["discipline", "id_aav", "nom", "taux_succes", "couverture", 
                   "utilisabilite", "alerte_difficile", "alerte_fragile", "alerte_inutilise"]
        return generate_csv_string(flat_data, columns)
    elif format == "pdf" or format == "json":
        data_to_return = {
            "discipline": id_cible,
            "nb_aavs": len(results),
            "aavs": results,
            "alertes": {
                "difficiles": [a.model_dump() for a in detecter_aavs_difficiles() if a.id_aav in aav_ids],
                "fragiles":   [a.model_dump() for a in detecter_aavs_fragiles()   if a.id_aav in aav_ids],
                "inutilises": [a.model_dump() for a in detecter_aavs_inutilises() if a.id_aav in aav_ids]
            }
        }
        if format == "pdf":
            return to_pdf(data_to_return, title=f"Rapport Discipline - {id_cible}")
        return data_to_return
    else:
        raise ValueError(f"Format de rapport inconnu : {format}")

def generer_rapport_personnalise(type, id_cible, debut, fin, format):
    if type == "aav":
        if not get_aav(int(id_cible)):
            return None
        data = collect_data_for_aav(int(id_cible), format)
    elif type == "student":
        if not get_student(int(id_cible)):
            return None
        data = collect_data_for_student(int(id_cible), format)
    elif type == "discipline":
        aavs = [aav for aav in get_all_aavs() if aav["discipline"] == id_cible]
        if not aavs:
            return None
        data = collect_data_for_discipline(id_cible, format)
    else:
        raise ValueError(f"Unknown report type: {type}")

    if not data:
        return None
        
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
