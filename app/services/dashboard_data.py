from database import get_db_session, EnseignantModel, AAVModel, MetriqueQualiteAAVModel, TentativeModel, OntologyReferenceModel
from typing import Optional
from database import from_json
from sqlalchemy import text

def get_enseignant(id_enseignant: int) -> Optional[dict]:
    with get_db_connection() as session:
        row = session.execute(
            text("SELECT * FROM enseignant WHERE id_enseignant = :id"),
            {"id": id_enseignant}
        ).fetchone()
        return dict(row._mapping) if row else None


def get_teacher_stats(teacher_id: int) -> Optional[dict]:
    """Calculates the overall performance of a teacher's students. It first identifies the subjects taught,
       then computes the average success rate and the total number of students involved."""
    with get_db_connection() as session:
        row = session.execute(
            text("SELECT discipline FROM enseignant WHERE id_enseignant = :id"),
            {"id": teacher_id}
        ).fetchone()
        if not row:
            return None

        res_discipline = from_json(row._mapping["discipline"])
        placeholders = ", ".join(f":d{i}" for i in range(len(res_discipline)))
        params = {f"d{i}": v for i, v in enumerate(res_discipline)}

        res = session.execute(
            text(f"""
                SELECT
                    COALESCE(AVG(metr.taux_succes_moyen), 0) AS moyenne,
                    COUNT(DISTINCT aav.id_aav)               AS nb_aav,
                    COUNT(DISTINCT tent.id_apprenant)         AS nb_apprenants
                FROM aav
                LEFT JOIN metrique_qualite_aav metr ON aav.id_aav = metr.id_aav
                LEFT JOIN tentative tent             ON tent.id_aav_cible = aav.id_aav
                WHERE aav.discipline IN ({placeholders})
                AND aav.is_active = 1
            """),
            params
        ).fetchone()

        result = dict(res._mapping)
        result["disciplines"] = res_discipline
        return result


def get_discipline_stats(discipline_name: str) -> dict:
    """Global discipline analysis: average success and resource coverage rate."""
    with get_db_connection() as session:
        res = session.execute(
            text("""
                SELECT
                    COALESCE(AVG(taux_succes_moyen), 0)          AS moyenne,
                    COALESCE(AVG(score_covering_ressources), 0)  AS moyenne_covering,
                    COUNT(aav.id_aav)                            AS nb
                FROM metrique_qualite_aav
                JOIN aav ON metrique_qualite_aav.id_aav = aav.id_aav
                WHERE discipline = :discipline
            """),
            {"discipline": discipline_name}
        ).fetchone()
        return dict(res._mapping)


def get_ontology_cov(id_reference: int) -> Optional[dict]:
    """
    Analyzes coverage for a specific ontology (curriculum).
    Retrieves the list of active AAV IDs from the ontology JSON.
    Calculates the average coverage score for these specific IDs.
    """
    with get_db_connection() as session:
        row = session.execute(
            text("SELECT aavs_ids_actifs FROM ontology_reference WHERE id_reference = :id"),
            {"id": id_reference}
        ).fetchone()
        if not row:
            return None

        res_ids = from_json(row._mapping["aavs_ids_actifs"])
        placeholders = ", ".join(f":id{i}" for i in range(len(res_ids)))
        params = {f"id{i}": v for i, v in enumerate(res_ids)}

        res = session.execute(
            text(f"""
                SELECT
                    COUNT(id_aav)                               AS nb_aav,
                    COALESCE(AVG(score_covering_ressources), 0) AS moyenne_covering
                FROM metrique_qualite_aav
                WHERE id_aav IN ({placeholders})
            """),
            params
        ).fetchone()
        return dict(res._mapping)