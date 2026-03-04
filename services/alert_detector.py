import statistics
from typing import List, Optional
from database import get_db_connection
from services.metric_calculator import calculer_taux_succes, get_all_aavs, count_attempts, get_all_attempts_for_aav

def get_apprenants_ontologie(ontologie_id: int) -> List[dict]:
    """Récupère tous les apprenants ayant une ontologie donnée."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM apprenant WHERE ontologie_reference_id = ?",
            (ontologie_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


def count_aavs_bloques(apprenant_id: int) -> int:
    """Compte le nombre d'AAVs non maîtrisés pour un apprenant."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM statut_apprentissage WHERE id_apprenant = ? AND niveau_maitrise < 1",
            (apprenant_id,)
        )
        return cursor.fetchone()[0]


def calculer_progression(apprenant_id: int) -> float:
    """Calcule la progression moyenne d'un apprenant (moyenne du niveau de maîtrise)."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT AVG(niveau_maitrise) FROM statut_apprentissage WHERE id_apprenant = ?",
            (apprenant_id,)
        )
        result = cursor.fetchone()[0]
        return float(result) if result is not None else 0.0


# ==============================================================
# FONCTIONS PRINCIPALES — Détection des alertes
# ==============================================================

def detecter_aavs_difficiles(seuil_taux_succes: float = 0.3) -> List[dict]:
    """AAV avec taux de succès moyen < seuil (trop difficiles pour les apprenants)."""
    problematiques = []
    for aav in get_all_aavs():
        taux = calculer_taux_succes(aav["id_aav"])
        if taux < seuil_taux_succes:
            problematiques.append({
                "id_aav": aav["id_aav"],
                "nom": aav["nom"],
                "taux_succes": taux,
                "nb_tentatives": count_attempts(aav["id_aav"]),
                "suggestion": "Revoir la définition ou ajouter des prérequis"
            })
    return problematiques


def detecter_apprenants_risque(id_ontologie: int, seuil_avancement: float = 0.1) -> List[dict]:
    """Apprenants avec progression anormalement faible."""
    risques = []
    for apprenant in get_apprenants_ontologie(id_ontologie):
        progression = calculer_progression(apprenant["id_apprenant"])
        if progression < seuil_avancement:
            risques.append({
                "id_apprenant": apprenant["id_apprenant"],
                "nom": apprenant["nom_utilisateur"],
                "progression": progression,
                "aavs_bloques": count_aavs_bloques(apprenant["id_apprenant"])
            })
    return risques


def detecter_aavs_inutilises() -> List[dict]:
    """Retourne les AAVs qui n'ont jamais été tentés (0 tentatives)."""
    return [
        {"id_aav": aav["id_aav"], "nom": aav["nom"]}
        for aav in get_all_aavs()
        if count_attempts(aav["id_aav"]) == 0
    ]


def detecter_aavs_fragiles(seuil_ecart_type: float = 0.35) -> List[dict]:
    """
    Retourne les AAVs dont les scores ont une forte variance.
    Un AAV est fragile si écart-type des scores > seuil (0.35 par défaut).
    """
    fragiles = []
    for aav in get_all_aavs():
        tentatives = get_all_attempts_for_aav(aav["id_aav"])
        scores = [t["score_obtenu"] for t in tentatives if t["score_obtenu"] is not None]
        if len(scores) < 2:
            continue
        ecart_type = statistics.stdev(scores)
        if ecart_type > seuil_ecart_type:
            fragiles.append({
                "id_aav": aav["id_aav"],
                "nom": aav["nom"],
                "ecart_type_scores": round(ecart_type, 4),
                "nb_tentatives": len(scores),
                "score_min": min(scores),
                "score_max": max(scores),
                "suggestion": "Les résultats sont très variables — revoir la difficulté ou les prérequis"
            })
    return fragiles