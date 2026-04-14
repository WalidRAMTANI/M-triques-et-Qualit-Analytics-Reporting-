from app.database import get_db_session, EnseignantModel, AAVModel, MetriqueQualiteAAVModel, TentativeModel, OntologyReferenceModel, get_db_connection, from_json
from typing import Optional
from sqlalchemy import func

def get_enseignant(id_enseignant: int) -> Optional[dict]:
    """
    Retrieve teacher information by ID.
    
    Fetches complete teacher details including discipline, email, and creation date.
    
    Args:
        id_enseignant (int): The ID of the teacher to retrieve.
    
    Returns:
        Optional[dict]: Teacher dictionary or None if not found.
    
    Example:
        >>> get_enseignant(1)
        {'id_enseignant': 1, 'nom': 'John Doe', 'discipline': 'Computer Science', ...}
    """
    with get_db_connection() as session:
        # Fetch teacher by ID
        enseignant = session.query(EnseignantModel).filter(
            EnseignantModel.id_enseignant == id_enseignant
        ).first()
        if not enseignant:
            return None
        return {
            "id_enseignant": enseignant.id_enseignant,
            "nom": enseignant.nom,
            "email": enseignant.email,
            "discipline": enseignant.discipline,
            "date_creation": enseignant.date_creation,
        }


def get_teacher_stats(teacher_id: int) -> Optional[dict]:
    """
    Calculate overall performance statistics for a teacher's students.
    """
    with get_db_connection() as session:
        # Get teacher and their disciplines
        enseignant = session.query(EnseignantModel).filter(
            EnseignantModel.id_enseignant == teacher_id
        ).first()
        if not enseignant:
            return None

        res_discipline = from_json(enseignant.discipline) if isinstance(enseignant.discipline, str) else enseignant.discipline
        if not res_discipline:
            res_discipline = []

        # Calculate statistics for teacher's disciplines
        # We need to joining AAV, Metrics and Tentatives
        stats = session.query(
            func.coalesce(func.avg(MetriqueQualiteAAVModel.taux_succes_moyen), 0).label("moyenne"),
            func.count(func.distinct(AAVModel.id_aav)).label("nb_aav"),
            func.count(func.distinct(TentativeModel.id_apprenant)).label("nb_apprenants")
        ).outerjoin(MetriqueQualiteAAVModel, AAVModel.id_aav == MetriqueQualiteAAVModel.id_aav)\
         .outerjoin(TentativeModel, TentativeModel.id_aav_cible == AAVModel.id_aav)\
         .filter(AAVModel.id_enseignant == teacher_id)\
         .filter(AAVModel.is_active == True).first()

        # Count active alerts for teacher's AAVs
        from app.database import AlerteQualiteModel
        alert_count = session.query(func.count(AlerteQualiteModel.id_alerte)).filter(
            AlerteQualiteModel.id_cible.in_(
                session.query(AAVModel.id_aav).filter(AAVModel.id_enseignant == teacher_id)
            ),
            AlerteQualiteModel.statut == "active"
        ).scalar() or 0

        return {
            "id_enseignant": enseignant.id_enseignant,
            "nom": enseignant.nom,
            "aavs_geres": stats.nb_aav if stats else 0,
            "apprenants_total": stats.nb_apprenants if stats else 0,
            "taux_succes_moyen": stats.moyenne if stats else 0.0,
            "alertes_actives": alert_count,
        }


def get_discipline_stats(discipline_name: str) -> dict:
    """
    Analyze global statistics for a specific discipline.
    """
    with get_db_connection() as session:
        # Calculate discipline-wide statistics
        # moyenne, nb_aav, nb_apprenants, nb_activites
        stats = session.query(
            func.coalesce(func.avg(MetriqueQualiteAAVModel.taux_succes_moyen), 0).label("moyenne"),
            func.count(func.distinct(AAVModel.id_aav)).label("nb_aav"),
            func.count(func.distinct(TentativeModel.id_apprenant)).label("nb_apprenants")
        ).outerjoin(MetriqueQualiteAAVModel, AAVModel.id_aav == MetriqueQualiteAAVModel.id_aav)\
         .outerjoin(TentativeModel, TentativeModel.id_aav_cible == AAVModel.id_aav)\
         .filter(AAVModel.discipline == discipline_name).first()

        # Recent activities count
        from app.database import ActivitePedagogiqueModel
        activites_count = session.query(func.count(ActivitePedagogiqueModel.id_activite)).filter(
            ActivitePedagogiqueModel.discipline == discipline_name
        ).scalar() or 0

        return {
            "discipline": discipline_name,
            "aavs_total": stats.nb_aav if stats else 0,
            "taux_succes_moyen": stats.moyenne if stats else 0.0,
            "apprenants_engages": stats.nb_apprenants if stats else 0,
            "activites_recentes": activites_count,
        }


def get_ontology_cov(id_reference: int) -> Optional[dict]:
    """
    Analyze curriculum coverage for a specific ontology reference.
    
    Retrieves all AAVs associated with an ontology and calculates overall
    coverage metrics for that curriculum.
    
    Args:
        id_reference (int): The ID of the ontology reference to analyze.
    
    Returns:
        Optional[dict]: Coverage statistics or None if ontology not found.
    
    Example:
        >>> get_ontology_cov(1)
        {'nb_aav': 3, 'moyenne_covering': 0.82}
    """
    with get_db_connection() as session:
        # Get the ontology reference
        ontologie = session.query(OntologyReferenceModel).filter(
            OntologyReferenceModel.id_reference == id_reference
        ).first()
        if not ontologie:
            return None

        # Extract active AAV IDs
        res_ids = from_json(ontologie.aavs_ids_actifs) if isinstance(ontologie.aavs_ids_actifs, str) else ontologie.aavs_ids_actifs

        # Calculate coverage statistics for this ontology
        stats = session.query(
            func.count(MetriqueQualiteAAVModel.id_aav).label("nb_aav"),
            func.coalesce(func.avg(MetriqueQualiteAAVModel.score_covering_ressources), 0).label("moyenne_covering")
        ).filter(MetriqueQualiteAAVModel.id_aav.in_(res_ids)).first()

        if stats:
            return {
                "nb_aav": stats.nb_aav,
                "moyenne_covering": stats.moyenne_covering,
            }
        return None