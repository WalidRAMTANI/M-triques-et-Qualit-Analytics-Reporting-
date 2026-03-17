import statistics
from typing import List, Optional
from datetime import datetime
from database import get_db_session, from_json, AAVModel, TentativeModel, MetriqueQualiteAAVModel, MetriqueQualiteAAVRepository
from sqlalchemy import func


def count_exercices(aav_id: int) -> int:
    """Counts the number of exercises for an AAV."""
    with get_db_session() as db:
        aav = db.get(AAVModel, aav_id)
        if not aav or not aav["ids_exercices"]:
            return 0
        return len(aav["ids_exercices"]) if isinstance(aav["ids_exercices"], list) else 0


def count_prompts(aav_id: int) -> int:
    """Counts the number of prompts for an AAV."""
    with get_db_session() as db:
        aav = db.get(AAVModel, aav_id)
        if not aav or not aav["prompts_fabrication_ids"]:
            return 0
        return len(aav["prompts_fabrication_ids"]) if isinstance(aav["prompts_fabrication_ids"], list) else 0


def diversity_evaluation_types(aav_id: int) -> int:
    """Counts the number of distinct evaluation types used for this AAV."""
    with get_db_session() as db:
        aav = db.get(AAVModel, aav_id)
        if not aav:
            return 0
        return 1 if aav["type_evaluation"] else 0


def get_all_attempts_for_aav(aav_id: int) -> List[TentativeModel]:
    """Retrieves all attempts for a given AAV."""
    with get_db_session() as db:
        return db.query(TentativeModel).filter(TentativeModel.id_aav_cible == aav_id).all()


def get_aav(aav_id: int) -> Optional[AAVModel]:
    """Retrieves an AAV by its ID. Returns None if not found."""
    with get_db_session() as db:
        return db.get(AAVModel, aav_id)


def get_all_aavs() -> List[AAVModel]:
    """Retrieves all active AAVs."""
    with get_db_session() as db:
        return db.query(AAVModel).filter(AAVModel.is_active == True).all()


def count_attempts(aav_id: int) -> int:
    """Counts the total number of attempts for an AAV."""
    with get_db_session() as db:
        return db.query(TentativeModel).filter(TentativeModel.id_aav_cible == aav_id).count()


def count_distinct_learners(aav_id: int) -> int:
    """Counts the number of distinct learners who attempted this AAV."""
    with get_db_session() as db:
        return db.query(func.count(func.distinct(TentativeModel.id_apprenant))).filter(TentativeModel.id_aav_cible == aav_id).scalar()


def calculer_couverture(aav_id: int) -> float:
    score = 0.0
    if count_exercices(aav_id) > 0:
        score += 0.4
    if count_prompts(aav_id) > 0:
        score += 0.3
    if diversity_evaluation_types(aav_id) >= 3:
        score += 0.3
    return score


def calculer_taux_succes(aav_id: int) -> float:
    tentatives = get_all_attempts_for_aav(aav_id)
    scores = [t["score_obtenu"] for t in tentatives if t["score_obtenu"] is not None]
    if len(scores) < 2:
        return statistics.mean(scores) if scores else 0.0
    mean = statistics.mean(scores)
    stdev = statistics.stdev(scores)
    filtered = [s for s in scores if abs(s - mean) <= 3 * stdev]
    return statistics.mean(filtered) if filtered else 0.0


def determiner_utilisabilite(aav_id: int) -> bool:
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


def get_metriques_by_aav(id_aav: int) -> Optional[MetriqueQualiteAAVModel]:
    """Retrieves the most recent quality metrics for a specific AAV."""
    with get_db_session() as db:
        return db.query(MetriqueQualiteAAVModel).filter(MetriqueQualiteAAVModel.id_aav == id_aav).order_by(MetriqueQualiteAAVModel.date_calcul.desc()).first()


def get_history(id_aav: int) -> List[MetriqueQualiteAAVModel]:
    """Retrieves the full history of calculated metrics for a specific AAV."""
    with get_db_session() as db:
        return db.query(MetriqueQualiteAAVModel).filter(MetriqueQualiteAAVModel.id_aav == id_aav).order_by(MetriqueQualiteAAVModel.date_calcul.desc()).all()


def get_all_metrics(filters: dict) -> List[MetriqueQualiteAAVModel]:
    """Retrieves the latest metrics for all AAVs in the database, with optional filters."""
    with get_db_session() as db:
        query = db.query(MetriqueQualiteAAVModel)
        
        if filters.get("score_covering_ressources") is not None:
            query = query.filter(MetriqueQualiteAAVModel.score_covering_ressources >= filters["score_covering_ressources"])
        if filters.get("taux_succes_moyen") is not None:
            query = query.filter(MetriqueQualiteAAVModel.taux_succes_moyen >= filters["taux_succes_moyen"])
        if filters.get("nb_tentatives_total") is not None:
            query = query.filter(MetriqueQualiteAAVModel.nb_tentatives_total >= filters["nb_tentatives_total"])
        if filters.get("nb_apprenants_distincts") is not None:
            query = query.filter(MetriqueQualiteAAVModel.nb_apprenants_distincts >= filters["nb_apprenants_distincts"])
        if filters.get("ecart_type_scores") is not None:
            query = query.filter(MetriqueQualiteAAVModel.ecart_type_scores >= filters["ecart_type_scores"])
            
        return query.all()
