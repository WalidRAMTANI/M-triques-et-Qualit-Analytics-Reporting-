import statistics
from typing import List, Optional
from database import get_db_connection
from services.metric_calculator import calculer_taux_succes, get_all_aavs, count_attempts, get_all_attempts_for_aav
from model.schemas import AAVDifficile, AAVInutilise, AAVFragile, ApprenantRisque
from sqlalchemy import text

def get_apprenants_ontologie(ontologie_id: int) -> List[dict]:
    """Retrieves all learners with a given ontology."""
    with get_db_connection() as session:
        result = session.execute(
            text("SELECT * FROM apprenant WHERE ontologie_reference_id = :ontologie_id"),
            {"ontologie_id": ontologie_id}
        )
        return [dict(row._mapping) for row in result.fetchall()]


def count_aavs_bloques(apprenant_id: int) -> int:
    """Counts the number of non-mastered AAVs for a learner."""
    with get_db_connection() as session:
        return session.execute(
            text("SELECT COUNT(*) FROM statut_apprentissage WHERE id_apprenant = :apprenant_id AND niveau_maitrise < 1"),
            {"apprenant_id": apprenant_id}
        ).scalar() or 0


def calculer_progression(apprenant_id: int) -> float:
    """Calculates the average progression of a learner (average mastery level)."""
    with get_db_connection() as session:
        result = session.execute(
            text("SELECT AVG(niveau_maitrise) FROM statut_apprentissage WHERE id_apprenant = :apprenant_id"),
            {"apprenant_id": apprenant_id}
        ).scalar()
        return float(result) if result is not None else 0.0

# ==============================================================
# FONCTIONS PRINCIPALES — Détection des alertes
# ==============================================================

def detecter_aavs_difficiles(seuil_taux_succes: float = 0.3) -> List[AAVDifficile]:
    """AAVs with an average success rate < threshold (too difficult for learners)."""
    problematiques = []
    for aav in get_all_aavs():
        taux = calculer_taux_succes(aav["id_aav"])
        if taux < seuil_taux_succes:
            problematiques.append(AAVDifficile(
                id_aav=aav["id_aav"],
                nom=aav["nom"],
                taux_succes=taux,
                nb_tentatives=count_attempts(aav["id_aav"]),
                suggestion="Revoir la définition ou ajouter des prérequis"
            ))
    return problematiques


def detecter_apprenants_risque(id_ontologie: int, seuil_avancement: float = 0.1) -> List[ApprenantRisque]:
    """Learners with an abnormally low progression."""
    risques = []
    for apprenant in get_apprenants_ontologie(id_ontologie):
        progression = calculer_progression(apprenant["id_apprenant"])
        if progression < seuil_avancement:
            risques.append(ApprenantRisque(
                id_apprenant=apprenant["id_apprenant"],
                nom=apprenant["nom_utilisateur"],
                progression=progression,
                aavs_bloques=count_aavs_bloques(apprenant["id_apprenant"])
            ))
    return risques


def detecter_aavs_inutilises() -> List[AAVInutilise]:
    """Returns AAVs that have never been attempted (0 attempts)."""
    return [
        AAVInutilise(
            id_aav=aav["id_aav"],
            nom=aav["nom"]
        )
        for aav in get_all_aavs()
        if count_attempts(aav["id_aav"]) == 0
    ]


def detecter_aavs_fragiles(seuil_ecart_type: float = 0.35) -> List[AAVFragile]:
    """
    Returns AAVs whose scores have a high variance.
    An AAV is fragile if the standard deviation of scores > threshold (0.35 by default).
    """
    fragiles = []
    for aav in get_all_aavs():
        tentatives = get_all_attempts_for_aav(aav["id_aav"])
        scores = [t["score_obtenu"] for t in tentatives if t["score_obtenu"] is not None]
        if len(scores) < 2:
            continue
        ecart_type = statistics.stdev(scores)
        if ecart_type > seuil_ecart_type:
            fragiles.append(AAVFragile(
                id_aav=aav["id_aav"],
                nom=aav["nom"],
                ecart_type_scores=round(ecart_type, 4),
                nb_tentatives=len(scores),
                score_min=min(scores),
                score_max=max(scores),
                suggestion="Les résultats sont très variables — revoir la difficulté ou les prérequis"
            ))
    return fragiles