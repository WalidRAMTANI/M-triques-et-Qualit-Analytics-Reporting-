import base64
from datetime import datetime
from database import get_db_connection
from services.metric_calculator import get_all_aavs, get_aav,calculer_couverture, calculer_taux_succes,determiner_utilisabilite, count_attempts, count_distinct_learners
from database import to_json, RapportRepository
from services.alert_detector import detecter_aavs_difficiles, detecter_aavs_fragiles,detecter_aavs_inutilises
from model.model import Rapport, LearnerBase
from model.schemas import AAVComparaison, ApprenantComparaison, RapportGlobalResponse
from typing import Optional, List

# helper for pdf
# C'est ici qu'on génère notre PDF "à la main" (sans librairie externe).
# Un fichier PDF n'est finalement qu'un gros fichier texte très structuré avec des "objets".
def to_pdf(data_dict, title="Rapport"):
    text = f"{title}\n\n"
    
    # Fonction récursive pour aplatir nos dictionnaires et listes en texte simple
    def format_dict(d, indent=0):
        res = ""
        prefix = " " * indent
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, (dict, list)):
                    res += f"{prefix}{k}:\n"
                    res += format_dict(v, indent + 4) # On indente plus profond
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
    
    # Très important: on convertit en pur ASCII. Certains lecteurs PDF crashent
    # si la police de base (Helvetica) reçoit des caractères Chelous ou des accents
    text = text.encode("ascii", "ignore").decode("ascii")
    
    # Dans la syntaxe PDF, les parenthèses () délimitent le texte, donc on doit échapper celles présentes
    text = text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
    lines = text.split('\n')
    
    # Voici le "Content Stream" : les instructions de dessins PDF!
    # BT = Begin Text, /F1 12 Tf = Font 1 Taille 12, Td = X,Y, TL = ligne spacing
    stream = "BT\n/F1 12 Tf\n50 800 Td\n15 TL\n"
    for line in lines[:50]: # On limite à 1 page grossièrement
        stream += f"({line}) Tj T*\n" # On dessine la ligne et on fait un retour chariot (T*)
    stream += "ET"
    
    # On prépare tous les "Objets" obligatoires du document (le catalogue, la page, la font...)
    obj1 = "<</Type /Catalog /Pages 2 0 R>>"
    obj2 = "<</Type /Pages /Kids [3 0 R] /Count 1>>"
    obj3 = "<</Type /Page /Parent 2 0 R /Resources <</Font <</F1 4 0 R>>>> /MediaBox [0 0 595 842] /Contents 5 0 R>>"
    obj4 = "<</Type /Font /Subtype /Type1 /BaseFont /Helvetica>>"
    obj5 = f"<</Length {len(stream)}>>\nstream\n{stream}\nendstream"
    
    objects = [obj1, obj2, obj3, obj4, obj5]
    
    # On commence à construire le binaire du fichier
    pdf_content = b"%PDF-1.4\n"
    offsets = []
    
    # On écrit chaque objet et on garde une trace exacte de son "offset" (la ligne d'octet où il commence). 
    for i, obj in enumerate(objects):
        offsets.append(len(pdf_content))
        pdf_content += f"{i+1} 0 obj\n{obj}\nendobj\n".encode('ascii')
        
    # Le système xref (cross-reference) est indispensable. C'est l'index que le logiciel PDF lit en premier.
    xref_pos = len(pdf_content)
    pdf_content += b"xref\n0 6\n0000000000 65535 f \n"
    for offset in offsets:
        pdf_content += f"{offset:010d} 00000 n \n".encode('ascii')
        
    # Fin du fichier, on dit au lecteur où trouver la xref table
    pdf_content += f"trailer\n<</Size 6 /Root 1 0 R>>\nstartxref\n{xref_pos}\n%%EOF\n".encode('ascii')
    
    # On encode cette bouillie binaire en Base64 pour que ça rentre gentillement dans notre colonne BDD de type String.
    return base64.b64encode(pdf_content).decode('ascii')

# helper for csv
def generate_csv_string(data, field):
    import csv, io
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=field)
    
    # On écrit d'abord la première ligne qui contient le nom des colonnes
    writer.writeheader()
    
    # Petite sécurité: csv.DictWriter a absolument besoin d'une LISTE DE DICTIONNAIRES.
    
    # Cas 1: L'utilisateur a passé juste un seul dictionnaire (une seule ligne), on s'assure d'en faire une liste
    if isinstance(data, dict):
        data = [data]
        
    # Cas 2: L'utilisateur a passé une liste toute simple (ex: [1, "Maths", 80]). 
    # Pour pas crasher, on la "zippe" automatiquement avec les `fieldnames` pour créer le dictionnaire manquant !
    elif isinstance(data, list) and len(data) > 0 and not isinstance(data[0], dict):
        # On regroupe chaque valeur avec sa colonne
        if len(data) == len(field):
            data = [dict(zip(field, data))]
    
    writer.writerows(data)
    
    # On renvoie tout sous forme d'une belle phrase texte au lieu d'un fichier pur
    return output.getvalue()

from sqlalchemy import text

def get_student(student_id: int) -> Optional[LearnerBase]:
    """Retrieves a learner by their ID. Returns None if not found."""
    with get_db_connection() as session:
        row = session.execute(
            text("SELECT * FROM apprenant WHERE id_apprenant = :student_id"),
            {"student_id": student_id}
        ).fetchone()
        if row:
            m = row._mapping
            return {
                "id_apprenant":      m["id_apprenant"],
                "nom":               m["nom_utilisateur"],
                "email":             m["email"],
                "date_inscription":  m["date_inscription"],
                "derniere_connexion": m["derniere_connexion"]
            }
        return None

def collect_data_for_aav(id_aav: int,format: str) -> AAVComparaison:
    """
    Collects all necessary data for a given AAV.
    """
    aav = get_aav(id_aav)
    if not aav:

        return None
    if format == "csv":
        return generate_csv_string([aav["id_aav"], aav["nom"], calculer_taux_succes(id_aav), calculer_couverture(id_aav), determiner_utilisabilite(id_aav), count_attempts(id_aav), count_distinct_learners(id_aav)], ["id_aav", "nom", "taux_succes", "couverture", "utilisabilite", "nb_tentatives", "nb_apprenants"])
    elif format == "pdf":
        data_dict = {"id_aav": aav["id_aav"], "nom": aav["nom"], "taux_succes": calculer_taux_succes(id_aav), "couverture": calculer_couverture(id_aav), "utilisabilite": determiner_utilisabilite(id_aav), "nb_tentatives": count_attempts(id_aav), "nb_apprenants": count_distinct_learners(id_aav)}
        return to_pdf(data_dict, title=f"Rapport AAV - {aav['nom']}")
    elif format == "json":
        return {"id_aav": aav["id_aav"],
        "nom": aav["nom"],
        "taux_succes": calculer_taux_succes(id_aav),
        "couverture": calculer_couverture(id_aav),
        "utilisabilite": determiner_utilisabilite(id_aav),
        "nb_tentatives": count_attempts(id_aav),
        "nb_apprenants": count_distinct_learners(id_aav)
    }
    else:
        raise ValueError(f"Format de rapport inconnu : {format}")
    
from sqlalchemy import text

def collect_data_for_student(id_cible: int, format: str) -> dict:
    """
    Collects all necessary data for a given learner.
    """
    student = get_student(id_cible)
    if not student:
        return None

    with get_db_connection() as session:
        tentatives = [
            dict(row._mapping)
            for row in session.execute(
                text("""
                    SELECT t.id_aav_cible AS id_aav, a.nom, t.score_obtenu, t.date_tentative
                    FROM tentative t
                    JOIN aav a ON t.id_aav_cible = a.id_aav
                    WHERE t.id_apprenant = :id_cible
                    ORDER BY t.date_tentative DESC
                """),
                {"id_cible": id_cible}
            ).fetchall()
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
            for t in tentatives
        ]
        return generate_csv_string(
            flat_data,
            ["id_apprenant", "nom_apprenant", "id_aav", "nom_aav", "score_obtenu", "date_tentative"]
        )

    elif format == "pdf":
        return to_pdf(tentatives, title=f"Rapport Apprenant - {nom_apprenant} ({id_apprenant})")

    elif format == "json":
        return {
            "id_apprenant":  id_apprenant,
            "nom":           nom_apprenant,
            "nb_tentatives": len(tentatives),
            "tentatives":    tentatives,
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
    elif format == "pdf":
        data_dict = {
            "discipline": id_cible,
            "nb_aavs": len(results),
            "aavs": results,
            "alertes": {
                "difficiles": [a.model_dump() for a in detecter_aavs_difficiles() if a.id_aav in aav_ids],
                "fragiles":   [a.model_dump() for a in detecter_aavs_fragiles()   if a.id_aav in aav_ids],
                "inutilises": [a.model_dump() for a in detecter_aavs_inutilises() if a.id_aav in aav_ids]
            }
        }
        return to_pdf(data_dict, title=f"Rapport Discipline - {id_cible}")
    elif format == "json":
        return {
            "discipline": id_cible,
            "aavs": results,
            "nb_aavs": len(results),
            "alertes": {
                "difficiles": [a.model_dump() for a in detecter_aavs_difficiles() if a.id_aav in aav_ids],
                "fragiles":   [a.model_dump() for a in detecter_aavs_fragiles()   if a.id_aav in aav_ids],
                "inutilises": [a.model_dump() for a in detecter_aavs_inutilises() if a.id_aav in aav_ids]
            }
        }
    else:
        raise ValueError(f"Format de rapport inconnu : {format}")

def generer_rapport_personnalise(type, id_cible, debut, fin, format):
    """
    Generate a personalized report based on the type of report, id_cible, date_debut, date_fin and format.
    Validates that id_cible exists before generating the report.
    Returns None if the target is not found.
    """
    if type == "aav":
        if not get_aav(int(id_cible)):
            return None
        data = collect_data_for_aav(int(id_cible), format)
    elif type == "student":
        if not get_student(int(id_cible)):
            return None
        data = collect_data_for_student(int(id_cible), format)
    elif type == "discipline":
        # Check that at least one AAV exists for this discipline
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
