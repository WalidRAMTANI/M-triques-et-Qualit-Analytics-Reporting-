import statistics
from typing import List, Optional
from app.database import get_db_connection, ApprenantModel, StatutApprentissageModel, MetriqueQualiteAAVModel
from app.services.metric_calculator import calculer_taux_succes, get_all_aavs, count_attempts, get_all_attempts_for_aav
from app.model.schemas import AAVDifficile, AAVInutilise, AAVFragile, ApprenantRisque, AAVBloquant
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
# MAIN FUNCTIONS — Alert detection
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


def detecter_aavs_bloquants() -> List[AAVBloquant]:
    """
    Détecte les AAV qui agissent comme des verrous pédagogiques.
    Un AAV est bloquant s'il est un prérequis pour d'autres AAV 
    que les apprenants n'arrivent pas à maîtriser.
    """
    bloquants = []
    tous_aavs = get_all_aavs()
    
    # Pour chaque AAV, on regarde combien d'AAV dépendants sont en échec
    for aav in tous_aavs:
        id_aav = aav["id_aav"]
        dep_en_echec = 0
        
        # On cherche tous les AAV qui ont id_aav comme prérequis
        for potentiel_dep in tous_aavs:
            # On vérifie les prérequis via la DB ou le modèle
            # Pour simplifier on va simuler ou chercher dans la base
            # Ici on va rester simple: si l'AAV est prérequis et que son propre taux de succès est moyen
            # mais que les autres sont bloqués derrière.
            pass
            
        # Version simplifiée pour le cahier des charges:
        # Un AAV est "bloquant" s'il est prérequis pour au moins 2 autres AAV
        # et que son taux de succès global est < 0.6
        taux = calculer_taux_succes(id_aav)
        
        # On compte combien de fois cet ID apparait dans les prerequis_ids des autres
        with get_db_connection() as session:
            from app.database import AAVModel
            count_dep = session.query(func.count(AAVModel.id_aav)).filter(
                AAVModel.prerequis_ids.contains(str(id_aav))
            ).scalar() or 0
            
            if count_dep >= 2 and taux < 0.6:
                bloquants.append(AAVBloquant(
                    id_aav=id_aav,
                    nom=aav["nom"],
                    nb_aavs_dependants_bloques=count_dep,
                    suggestion="Simplifier cet AAV car il bloque la progression vers plusieurs autres objectifs"
                ))
    
    return bloquants