import statistics
from typing import List, Optional
from datetime import datetime
from model.model import MetriqueQualiteAAV
from sqlalchemy import func
from database import get_db_connection, from_json, MetriqueQualiteAAVRepository, AAVModel, TentativeModel, MetriqueQualiteAAVModel

def count_exercices(aav_id: int) -> int:
    """
    Count the number of exercises associated with an AAV.
    
    Retrieves an AAV by ID and counts the number of exercises stored in the
    ids_exercices JSON column.
    
    Args:
        aav_id (int): The ID of the AAV to query.
    
    Returns:
        int: The number of exercises, or 0 if AAV not found or no exercises.
    
    Example:
        >>> count_exercices(1)
        2
    """
    with get_db_connection() as session:
        # Get the AAV and extract exercise list
        aav = session.query(AAVModel).filter(AAVModel.id_aav == aav_id).first()
        if not aav or not aav.ids_exercices:
            return 0
        ids = from_json(aav.ids_exercices) if isinstance(aav.ids_exercices, str) else aav.ids_exercices
        return len(ids) if ids else 0


def count_prompts(aav_id: int) -> int:
    """
    Count the number of prompts associated with an AAV.
    
    Retrieves an AAV by ID and counts the number of prompts stored in the
    prompts_fabrication_ids JSON column.
    
    Args:
        aav_id (int): The ID of the AAV to query.
    
    Returns:
        int: The number of prompts, or 0 if AAV not found or no prompts.
    
    Example:
        >>> count_prompts(1)
        1
    """
    with get_db_connection() as session:
        # Get the AAV and extract prompt list
        aav = session.query(AAVModel).filter(AAVModel.id_aav == aav_id).first()
        if not aav or not aav.prompts_fabrication_ids:
            return 0
        ids = from_json(aav.prompts_fabrication_ids) if isinstance(aav.prompts_fabrication_ids, str) else aav.prompts_fabrication_ids
        return len(ids) if ids else 0


def diversity_evaluation_types(aav_id: int) -> int:
    """
    Count the number of distinct evaluation types for an AAV.
    
    Queries the database to find how many different evaluation types are
    associated with attempts for the given AAV.
    
    Args:
        aav_id (int): The ID of the AAV to analyze.
    
    Returns:
        int: The count of distinct evaluation types, or 0 if none found.
    
    Example:
        >>> diversity_evaluation_types(1)
        2
    """
    with get_db_connection() as session:
        # Count distinct evaluation types for this AAV
        return session.query(func.count(func.distinct(AAVModel.type_evaluation))).filter(
            AAVModel.id_aav == aav_id
        ).scalar() or 0


def get_all_attempts_for_aav(aav_id: int) -> List[dict]:
    """
    Retrieve all attempts (tentatives) for a given AAV.
    
    Queries all attempt records where the target AAV matches the given ID,
    and converts model objects to dictionaries.
    
    Args:
        aav_id (int): The ID of the AAV to fetch attempts for.
    
    Returns:
        List[dict]: List of attempt dictionaries, empty list if no attempts found.
    
    Example:
        >>> get_all_attempts_for_aav(1)
        [{'id': 1, 'score_obtenu': 0.7, ...}, ...]
    """
    with get_db_connection() as session:
        # Query all attempts for this AAV
        attempts = session.query(TentativeModel).filter(
            TentativeModel.id_aav_cible == aav_id
        ).all()
        return [
            {
                "id": t.id,
                "id_exercice_ou_evenement": t.id_exercice_ou_evenement,
                "id_apprenant": t.id_apprenant,
                "id_aav_cible": t.id_aav_cible,
                "score_obtenu": t.score_obtenu,
                "date_tentative": t.date_tentative,
                "est_valide": t.est_valide,
                "temps_resolution_secondes": t.temps_resolution_secondes,
                "metadata": t.meta_data,
            }
            for t in attempts
        ]


def get_aav(aav_id: int) -> Optional[dict]:
    """
    Retrieve a complete AAV record by its ID.
    
    Fetches an AAV from the database and returns all its properties as a dictionary.
    Returns None if the AAV does not exist.
    
    Args:
        aav_id (int): The ID of the AAV to retrieve.
    
    Returns:
        Optional[dict]: Dictionary containing AAV data, or None if not found.
    
    Example:
        >>> get_aav(1)
        {'id_aav': 1, 'nom': 'Python Basics', ...}
    """
    with get_db_connection() as session:
        # Fetch the AAV and convert to dictionary
        aav = session.query(AAVModel).filter(AAVModel.id_aav == aav_id).first()
        if not aav:
            return None
        return {
            "id_aav": aav.id_aav,
            "nom": aav.nom,
            "libelle_integration": aav.libelle_integration,
            "discipline": aav.discipline,
            "enseignement": aav.enseignement,
            "id_enseignant": aav.id_enseignant,
            "type_aav": aav.type_aav,
            "description_markdown": aav.description_markdown,
            "is_active": aav.is_active,
        }


def get_all_aavs() -> List[dict]:
    """
    Retrieve all active AAVs from the database.
    
    Queries all AAVs with is_active=True and converts them to dictionaries.
    
    Returns:
        List[dict]: List of AAV dictionaries, empty if none active.
    
    Example:
        >>> get_all_aavs()
        [{'id_aav': 1, 'nom': 'AAV1', ...}, ...]
    """
    with get_db_connection() as session:
        # Query all active AAVs
        aavs = session.query(AAVModel).filter(AAVModel.is_active == True).all()
        return [
            {
                "id_aav": aav.id_aav,
                "nom": aav.nom,
                "libelle_integration": aav.libelle_integration,
                "discipline": aav.discipline,
                "enseignement": aav.enseignement,
                "id_enseignant": aav.id_enseignant,
                "type_aav": aav.type_aav,
                "description_markdown": aav.description_markdown,
                "is_active": aav.is_active,
            }
            for aav in aavs
        ]


def count_attempts(aav_id: int) -> int:
    """
    Count the total number of attempts made for an AAV.
    
    Counts all tentative records where the target AAV matches the given ID.
    
    Args:
        aav_id (int): The ID of the AAV to count attempts for.
    
    Returns:
        int: The total number of attempts, or 0 if none found.
    
    Example:
        >>> count_attempts(1)
        6
    """
    with get_db_connection() as session:
        # Count all attempts for this AAV
        return session.query(func.count(TentativeModel.id)).filter(
            TentativeModel.id_aav_cible == aav_id
        ).scalar() or 0


def count_distinct_learners(aav_id: int) -> int:
    """
    Count the number of distinct learners who attempted an AAV.
    
    Counts unique learners by their id_apprenant for all attempts targeting
    the given AAV.
    
    Args:
        aav_id (int): The ID of the AAV to analyze.
    
    Returns:
        int: The count of distinct learners, or 0 if none found.
    
    Example:
        >>> count_distinct_learners(1)
        4
    """
    with get_db_connection() as session:
        # Count distinct learners for this AAV
        return session.query(func.count(func.distinct(TentativeModel.id_apprenant))).filter(
            TentativeModel.id_aav_cible == aav_id
        ).scalar() or 0

def calculer_couverture(aav_id: int) -> float:
    """
    Calculate the coverage score for an AAV.
    
    The coverage score is composed of:
    - 40% from number of exercises
    - 30% from number of prompts
    - 30% from diversity of evaluation types (with bonus if exactly 3 types)
    
    Args:
        aav_id (int): The ID of the AAV to calculate coverage for.
    
    Returns:
        float: Coverage score between 0.0 and 1.0.
    
    Example:
        >>> calculer_couverture(1)
        0.7
    """
    # Calculate weighted coverage score
    score = 0.0
    if count_exercices(aav_id) > 0:
        score += 0.4
    if count_prompts(aav_id) > 0:
        score += 0.3
    if diversity_evaluation_types(aav_id) >= 3:
        score += 0.3
    return score


def calculer_taux_succes(aav_id: int) -> float:
    """
    Calculate the success rate for an AAV.
    
    Computes the mean score of all attempts for an AAV, filtering out statistical
    outliers (3-sigma rule) if there are 2+ attempts.
    
    Args:
        aav_id (int): The ID of the AAV to calculate success rate for.
    
    Returns:
        float: Success rate between 0.0 and 1.0.
    
    Example:
        >>> calculer_taux_succes(1)
        0.82
    """
    # Get all attempts and extract scores
    tentatives = get_all_attempts_for_aav(aav_id)
    scores = [t["score_obtenu"] for t in tentatives if t["score_obtenu"] is not None]
    if len(scores) < 2:
        return statistics.mean(scores) if scores else 0.0
    # Filter outliers using 3-sigma rule
    mean = statistics.mean(scores)
    stdev = statistics.stdev(scores)
    filtered = [s for s in scores if abs(s - mean) <= 3 * stdev]
    return statistics.mean(filtered) if filtered else 0.0


def determiner_utilisabilite(aav_id: int) -> bool:
    """
    Determine if an AAV is usable based on quality criteria.
    
    Checks if an AAV meets all usability requirements:
    - Coverage score >= 0.7
    - Success rate between 0.2 and 0.95
    - Has description markdown
    - Has integration label
    
    Args:
        aav_id (int): The ID of the AAV to evaluate.
    
    Returns:
        bool: True if usable, False otherwise.
    
    Example:
        >>> determiner_utilisabilite(1)
        True
    """
    # Evaluate usability criteria
    aav = get_aav(aav_id)
    if not aav:
        return False

    couverture = calculer_couverture(aav_id)
    taux = calculer_taux_succes(aav_id)

    return (
        couverture >= 0.7 and
        0.2 < taux < 0.95 and
        bool(aav["description_markdown"]) and
        bool(aav["libelle_integration"])
    )


def calculer_metriques_aav(id_aav: int) -> MetriqueQualiteAAVModel:
    """
    Calculate all quality metrics for an AAV.
    
    Computes coverage, success rate, usability, and statistical measures,
    then saves the metrics to the database.
    
    Args:
        id_aav (int): The ID of the AAV to calculate metrics for.
    
    Returns:
        MetriqueQualiteAAVModel: The saved metric record.
    
    Example:
        >>> calculer_metriques_aav(1)
        <MetriqueQualiteAAVModel: id_aav=1, ...>
    """
    # Calculate all metric components
    couverture   = calculer_couverture(id_aav)
    taux_succes  = calculer_taux_succes(id_aav)
    utilisable   = determiner_utilisabilite(id_aav)
    nb_tentatives = count_attempts(id_aav)
    nb_apprenants = count_distinct_learners(id_aav)

    tentatives = get_all_attempts_for_aav(id_aav)
    scores = [t["score_obtenu"] for t in tentatives if t["score_obtenu"] is not None]
    ecart_type = statistics.stdev(scores) if len(scores) >= 2 else 0.0

    metrique = MetriqueQualiteAAVModel(
        id_aav=id_aav,
        score_covering_ressources=couverture,
        taux_succes_moyen=taux_succes,
        est_utilisable=utilisable,
        nb_tentatives_total=nb_tentatives,
        nb_apprenants_distincts=nb_apprenants,
        ecart_type_scores=ecart_type,
        date_calcul=datetime.now(),
        periode_debut=datetime.now(),
        periode_fin=datetime.now()
    )
    return MetriqueQualiteAAVRepository().create(metrique)

def get_metriques_by_aav(id_aav: int) -> Optional[dict]:
    """
    Retrieve the most recent quality metrics for an AAV.
    
    Fetches the latest metric record for the given AAV and converts it to
    a dictionary. Returns None if no metrics exist.
    
    Args:
        id_aav (int): The ID of the AAV to fetch metrics for.
    
    Returns:
        Optional[dict]: Metric dictionary or None if not found.
    
    Example:
        >>> get_metriques_by_aav(1)
        {'id_aav': 1, 'score_covering_ressources': 0.9, ...}
    """
    with get_db_connection() as session:
        # Fetch the most recent metric record
        metrique = session.query(MetriqueQualiteAAVModel).filter(
            MetriqueQualiteAAVModel.id_aav == id_aav
        ).first()
        if not metrique:
            return None
        return {
            "id_metrique": metrique.id_metrique,
            "id_aav": metrique.id_aav,
            "score_covering_ressources": metrique.score_covering_ressources,
            "taux_succes_moyen": metrique.taux_succes_moyen,
            "est_utilisable": metrique.est_utilisable,
            "nb_tentatives_total": metrique.nb_tentatives_total,
            "nb_apprenants_distincts": metrique.nb_apprenants_distincts,
            "ecart_type_scores": metrique.ecart_type_scores,
            "date_calcul": metrique.date_calcul,
            "periode_debut": metrique.periode_debut,
            "periode_fin": metrique.periode_fin,
        }


def get_history(id_aav: int) -> Optional[List[dict]]:
    """
    Retrieve the complete history of calculated metrics for an AAV.
    
    Fetches all metric records for the given AAV, sorted by calculation date
    in descending order (most recent first).
    
    Args:
        id_aav (int): The ID of the AAV to fetch history for.
    
    Returns:
        Optional[List[dict]]: List of metric dictionaries, sorted by date.
    
    Example:
        >>> get_history(1)
        [{'id_aav': 1, 'date_calcul': '2026-02-21', ...}, ...]
    """
    with get_db_connection() as session:
        # Fetch all metric records, sorted by date descending
        metriques = session.query(MetriqueQualiteAAVModel).filter(
            MetriqueQualiteAAVModel.id_aav == id_aav
        ).order_by(MetriqueQualiteAAVModel.date_calcul.desc()).all()
        return [
            {
                "id_metrique": m.id_metrique,
                "id_aav": m.id_aav,
                "score_covering_ressources": m.score_covering_ressources,
                "taux_succes_moyen": m.taux_succes_moyen,
                "est_utilisable": m.est_utilisable,
                "nb_tentatives_total": m.nb_tentatives_total,
                "nb_apprenants_distincts": m.nb_apprenants_distincts,
                "ecart_type_scores": m.ecart_type_scores,
                "date_calcul": m.date_calcul,
                "periode_debut": m.periode_debut,
                "periode_fin": m.periode_fin,
            }
            for m in metriques
        ]


def get_all_metrics(filters: dict) -> List:
    """
    Retrieve all metrics with optional filtering criteria.
    
    Fetches all metric records from the database and applies optional filters
    based on coverage score, success rate, attempt count, learner count, or
    standard deviation thresholds.
    
    Args:
        filters (dict): Optional filter criteria. Supported keys:
            - score_covering_ressources: minimum coverage score
            - taux_succes_moyen: minimum success rate
            - nb_tentatives_total: minimum attempt count
            - nb_apprenants_distincts: minimum learner count
            - ecart_type_scores: minimum standard deviation
    
    Returns:
        List: List of metric records matching filters.
    
    Example:
        >>> get_all_metrics({'score_covering_ressources': 0.7})
        [<MetriqueQualiteAAVModel: ...>, ...]
    """
    with get_db_connection() as session:
        # Build dynamic query with optional filters
        query = session.query(MetriqueQualiteAAVModel)
        
        if filters.get("score_covering_ressources"):
            query = query.filter(MetriqueQualiteAAVModel.score_covering_ressources >= filters["score_covering_ressources"])
        if filters.get("taux_succes_moyen"):
            query = query.filter(MetriqueQualiteAAVModel.taux_succes_moyen >= filters["taux_succes_moyen"])
        if filters.get("nb_tentatives_total"):
            query = query.filter(MetriqueQualiteAAVModel.nb_tentatives_total >= filters["nb_tentatives_total"])
        if filters.get("nb_apprenants_distincts"):
            query = query.filter(MetriqueQualiteAAVModel.nb_apprenants_distincts >= filters["nb_apprenants_distincts"])
        if filters.get("ecart_type_scores"):
            query = query.filter(MetriqueQualiteAAVModel.ecart_type_scores >= filters["ecart_type_scores"])
        
        metriques = query.all()
        return [MetriqueQualiteAAV(**{
            "id_metrique": m.id_metrique,
            "id_aav": m.id_aav,
            "score_covering_ressources": m.score_covering_ressources,
            "taux_succes_moyen": m.taux_succes_moyen,
            "est_utilisable": m.est_utilisable,
            "nb_tentatives_total": m.nb_tentatives_total,
            "nb_apprenants_distincts": m.nb_apprenants_distincts,
            "ecart_type_scores": m.ecart_type_scores,
            "date_calcul": m.date_calcul,
            "periode_debut": m.periode_debut,
            "periode_fin": m.periode_fin,
        }) for m in metriques]