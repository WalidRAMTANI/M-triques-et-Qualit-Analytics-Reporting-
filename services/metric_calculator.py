import statistics
from typing import List, Optional
from datetime import datetime
from database import get_db_connection, from_json
from model import MetriqueQualiteAAV
from database import MetriqueQualiteAAVRepository


def count_exercices(aav_id: int) -> int:
    """Compte le nombre d'exercices d'un AAV (stockés en JSON dans la colonne ids_exercices)."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ids_exercices FROM aav WHERE id_aav = ?", (aav_id,))
        row = cursor.fetchone()
        if not row or not row["ids_exercices"]:
            return 0
        ids = from_json(row["ids_exercices"])
        return len(ids) if ids else 0


def count_prompts(aav_id: int) -> int:
    """Compte le nombre de prompts d'un AAV (stockés en JSON dans prompts_fabrication_ids)."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT prompts_fabrication_ids FROM aav WHERE id_aav = ?", (aav_id,))
        row = cursor.fetchone()
        if not row or not row["prompts_fabrication_ids"]:
            return 0
        ids = from_json(row["prompts_fabrication_ids"])
        return len(ids) if ids else 0


def diversity_evaluation_types(aav_id: int) -> int:
    """Compte le nombre de types d'évaluation distincts utilisés sur cet AAV."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(DISTINCT a.type_evaluation)
            FROM aav a
            WHERE a.id_aav = ?
        """, (aav_id,))
        result = cursor.fetchone()
        return result[0] if result else 0


def get_all_attempts_for_aav(aav_id: int) -> List[dict]:
    """Récupère toutes les tentatives pour un AAV donné."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tentative WHERE id_aav_cible = ?",
            (aav_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_aav(aav_id: int) -> Optional[dict]:
    """Récupère un AAV par son ID. Retourne None si introuvable."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM aav WHERE id_aav = ?", (aav_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_aavs() -> List[dict]:
    """Récupère tous les AAVs actifs."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM aav WHERE is_active = 1")
        return [dict(row) for row in cursor.fetchall()]


def count_attempts(aav_id: int) -> int:
    """Compte le nombre total de tentatives pour un AAV."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM tentative WHERE id_aav_cible = ?",
            (aav_id,)
        )
        return cursor.fetchone()[0]


def count_distinct_learners(aav_id: int) -> int:
    """Compte le nombre d'apprenants distincts ayant tenté cet AAV."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(DISTINCT id_apprenant) FROM tentative WHERE id_aav_cible = ?",
            (aav_id,)
        )
        return cursor.fetchone()[0]


def calculer_couverture(aav_id: int) -> float:
    """
    Mesure la couverture des ressources pour un AAV.
    - Présence d'exercices : 0.4 points
    - Présence de prompts  : 0.3 points
    - Diversité des types d'évaluation >= 3 : 0.3 points
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
    Un AAV est utilisable si :
    - couverture >= 0.7
    - taux_succes_moyen > 0.2 (pas impossible)
    - taux_succes_moyen < 0.95 (pas trivial)
    - définition claire (champs obligatoires présents)
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
    Calcule toutes les métriques pour un AAV et les sauvegarde
    dans la table metrique_qualite_aav.

    Retourne un MetriqueQualiteAAV avec toutes les métriques calculées.
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
        date_calcul=datetime.now()
    )
    return MetriqueQualiteAAVRepository().create(metrique)