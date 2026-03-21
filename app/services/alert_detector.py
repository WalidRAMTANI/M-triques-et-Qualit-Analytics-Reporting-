import statistics
from typing import List, Optional
from database import get_db_connection, ApprenantModel, StatutApprentissageModel, MetriqueQualiteAAVModel
from services.metric_calculator import calculer_taux_succes, get_all_aavs, count_attempts, get_all_attempts_for_aav
from model.schemas import AAVDifficile, AAVInutilise, AAVFragile, ApprenantRisque
from sqlalchemy import func

def get_apprenants_ontologie(ontologie_id: int) -> List[dict]:
    """
    Retrieve all learners assigned to a specific ontology.
    
    Fetches all learner records where the ontology_reference_id matches,
    and converts them to dictionaries.
    
    Args:
        ontologie_id (int): The ID of the ontology reference.
    
    Returns:
        List[dict]: List of learner dictionaries.
    
    Example:
        >>> get_apprenants_ontologie(1)
        [{'id_apprenant': 1, 'nom_utilisateur': 'Alice', ...}, ...]
    """
    with get_db_connection() as session:
        # Query all learners for this ontology
        apprenants = session.query(ApprenantModel).filter(
            ApprenantModel.ontologie_reference_id == ontologie_id
        ).all()
        return [
            {
                "id_apprenant": a.id_apprenant,
                "nom_utilisateur": a.nom_utilisateur,
                "email": a.email,
                "ontologie_reference_id": a.ontologie_reference_id,
            }
            for a in apprenants
        ]


def count_aavs_bloques(apprenant_id: int) -> int:
    """
    Count the number of non-mastered AAVs for a learner.
    
    Counts learning status records where the learner has not mastered
    (niveau_maitrise < 1) the specific AAV.
    
    Args:
        apprenant_id (int): The ID of the learner.
    
    Returns:
        int: Number of non-mastered AAVs, or 0 if none.
    
    Example:
        >>> count_aavs_bloques(1)
        3
    """
    with get_db_connection() as session:
        # Count unmastered AAVs for this learner
        return session.query(func.count(StatutApprentissageModel.id)).filter(
            StatutApprentissageModel.id_apprenant == apprenant_id,
            StatutApprentissageModel.niveau_maitrise < 1
        ).scalar() or 0


def calculer_progression(apprenant_id: int) -> float:
    """
    Calculate the average learning progression for a learner.
    
    Computes the mean mastery level across all learning status records
    for the given learner.
    
    Args:
        apprenant_id (int): The ID of the learner.
    
    Returns:
        float: Average mastery level between 0.0 and 1.0, or 0.0 if no data.
    
    Example:
        >>> calculer_progression(1)
        0.65
    """
    with get_db_connection() as session:
        # Calculate average mastery level
        result = session.query(
            func.avg(StatutApprentissageModel.niveau_maitrise)
        ).filter(
            StatutApprentissageModel.id_apprenant == apprenant_id
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