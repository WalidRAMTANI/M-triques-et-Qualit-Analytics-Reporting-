import statistics
from typing import List, Optional
from datetime import datetime
from database import get_db_connection, from_json
from model.model import MetriqueQualiteAAV
from database import MetriqueQualiteAAVRepository
from sqlalchemy import text

def count_exercices(aav_id: int) -> int:
    """Counts the number of exercises for an AAV (stored as JSON in the ids_exercices column)."""
    with get_db_connection() as session:
        row = session.execute(
            text("SELECT ids_exercices FROM aav WHERE id_aav = :aav_id"),
            {"aav_id": aav_id}
        ).fetchone()
        if not row or not row._mapping["ids_exercices"]:
            return 0
        ids = from_json(row._mapping["ids_exercices"])
        return len(ids) if ids else 0


def count_prompts(aav_id: int) -> int:
    """Counts the number of prompts for an AAV (stored as JSON in prompts_fabrication_ids)."""
    with get_db_connection() as session:
        row = session.execute(
            text("SELECT prompts_fabrication_ids FROM aav WHERE id_aav = :aav_id"),
            {"aav_id": aav_id}
        ).fetchone()
        if not row or not row._mapping["prompts_fabrication_ids"]:
            return 0
        ids = from_json(row._mapping["prompts_fabrication_ids"])
        return len(ids) if ids else 0


def diversity_evaluation_types(aav_id: int) -> int:
    """Counts the number of distinct evaluation types used for this AAV."""
    with get_db_connection() as session:
        return session.execute(
            text("SELECT COUNT(DISTINCT type_evaluation) FROM aav WHERE id_aav = :aav_id"),
            {"aav_id": aav_id}
        ).scalar() or 0


def get_all_attempts_for_aav(aav_id: int) -> List[dict]:
    """Retrieves all attempts for a given AAV."""
    with get_db_connection() as session:
        result = session.execute(
            text("SELECT * FROM tentative WHERE id_aav_cible = :aav_id"),
            {"aav_id": aav_id}
        )
        return [dict(row._mapping) for row in result.fetchall()]


def get_aav(aav_id: int) -> Optional[dict]:
    """Retrieves an AAV by its ID. Returns None if not found."""
    with get_db_connection() as session:
        row = session.execute(
            text("SELECT * FROM aav WHERE id_aav = :aav_id"),
            {"aav_id": aav_id}
        ).fetchone()
        return dict(row._mapping) if row else None


def get_all_aavs() -> List[dict]:
    """Retrieves all active AAVs."""
    with get_db_connection() as session:
        result = session.execute(
            text("SELECT * FROM aav WHERE is_active = 1")
        )
        return [dict(row._mapping) for row in result.fetchall()]


def count_attempts(aav_id: int) -> int:
    """Counts the total number of attempts for an AAV."""
    with get_db_connection() as session:
        return session.execute(
            text("SELECT COUNT(*) FROM tentative WHERE id_aav_cible = :aav_id"),
            {"aav_id": aav_id}
        ).scalar() or 0


def count_distinct_learners(aav_id: int) -> int:
    """Counts the number of distinct learners who attempted this AAV."""
    with get_db_connection() as session:
        return session.execute(
            text("SELECT COUNT(DISTINCT id_apprenant) FROM tentative WHERE id_aav_cible = :aav_id"),
            {"aav_id": aav_id}
        ).scalar() or 0

def calculer_couverture(aav_id: int) -> float:
    """
    Measures resource coverage for an AAV.
    - Presence of exercises: 0.4 points
    - Presence of prompts: 0.3 points
    - Diversity of evaluation types >= 3: 0.3 points
    """
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
    """
    An AAV is usable if:
    - coverage >= 0.7
    - average_success_rate > 0.2 (not impossible)
    - average_success_rate < 0.95 (not trivial)
    - clear definition (mandatory fields present)
    """
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


def calculer_metriques_aav(id_aav: int) -> MetriqueQualiteAAV:
    """
    Calculates all metrics for an AAV and saves them
    in the metrique_qualite_aav table.

    Returns a MetriqueQualiteAAV with all calculated metrics.
    """
    couverture   = calculer_couverture(id_aav)
    taux_succes  = calculer_taux_succes(id_aav)
    utilisable   = determiner_utilisabilite(id_aav)
    nb_tentatives = count_attempts(id_aav)
    nb_apprenants = count_distinct_learners(id_aav)

    tentatives = get_all_attempts_for_aav(id_aav)
    scores = [t["score_obtenu"] for t in tentatives if t["score_obtenu"] is not None]
    ecart_type = statistics.stdev(scores) if len(scores) >= 2 else 0.0


    metrique = MetriqueQualiteAAV(
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
    Retrieves the most recent quality metrics for a specific AAV.
    Returns a dictionary of columns or None if not found.
    """
    with get_db_connection() as session:
        row = session.execute(
            text("SELECT * FROM metrique_qualite_aav WHERE id_aav = :id_aav"),
            {"id_aav": id_aav}
        ).fetchone()
        return dict(row._mapping) if row else None


def get_history(id_aav: int) -> Optional[List[dict]]:
    """
    Retrieves the full history of calculated metrics for a specific AAV,
    sorted by calculation date (most recent first).
    """
    with get_db_connection() as session:
        rows = session.execute(
            text("SELECT * FROM metrique_qualite_aav WHERE id_aav = :id_aav ORDER BY date_calcul DESC"),
            {"id_aav": id_aav}
        ).fetchall()
        return [dict(r._mapping) for r in rows]


def get_all_metrics(filters: dict) -> List:
    """
    Retrieves the latest metrics for all AAVs in the database, with optional filters.
    """
    params = {
        "score_covering_ressources": filters.get("score_covering_ressources") or 0,
        "taux_succes_moyen":         filters.get("taux_succes_moyen")         or 0,
        "nb_tentatives_total":       filters.get("nb_tentatives_total")       or 0,
        "nb_apprenants_distincts":   filters.get("nb_apprenants_distincts")   or 0,
        "ecart_type_scores":         filters.get("ecart_type_scores")         or 0,
    }

    with get_db_connection() as session:
        rows = session.execute(
            text("""
                SELECT * FROM metrique_qualite_aav
                WHERE score_covering_ressources >= :score_covering_ressources
                AND   taux_succes_moyen         >= :taux_succes_moyen
                AND   nb_tentatives_total       >= :nb_tentatives_total
                AND   nb_apprenants_distincts   >= :nb_apprenants_distincts
                AND   ecart_type_scores         >= :ecart_type_scores
            """),
            params
        ).fetchall()
        return [MetriqueQualiteAAV(**dict(r._mapping)) for r in rows]