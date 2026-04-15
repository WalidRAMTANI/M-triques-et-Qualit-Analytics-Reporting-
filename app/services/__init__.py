from .maitrise import calculer_maitrise
from app.database import (
    get_db_connection, TentativeExerciceModel, ExerciceInstanceModel
)
from sqlalchemy import and_

def calculer_maitrise_reelle(id_apprenant: int, id_aav: int) -> float:
    """Calcule la maîtrise réelle basée sur les tentatives passées."""
    with get_db_connection() as session:
        # TentativeExerciceModel n'a pas id_aav directement ;
        # on filtre via la jointure avec ExerciceInstanceModel
        tentatives = (
            session.query(TentativeExerciceModel)
            .join(
                ExerciceInstanceModel,
                ExerciceInstanceModel.id_exercice == TentativeExerciceModel.id_exercice
            )
            .filter(
                and_(
                    TentativeExerciceModel.id_apprenant == id_apprenant,
                    ExerciceInstanceModel.id_aav_cible == id_aav
                )
            )
            .order_by(TentativeExerciceModel.date_tentative.asc())
            .all()
        )

        if not tentatives:
            return 0.0

        scores = [t.score_obtenu for t in tentatives]
        return calculer_maitrise(scores, seuil_succes=0.7, nombre_succes_consecutifs=3)

def determiner_difficulte_cible(maitrise: float) -> str:
    if maitrise < 0.4: return "debutant"
    if maitrise < 0.8: return "intermediaire"
    return "avance"

def selectionner_sequence_exercices(id_apprenant: int, id_aav: int, nb_exercices: int = 3) -> list:
    """Sélectionne une suite d'exercices adaptés."""
    maitrise = calculer_maitrise_reelle(id_apprenant, id_aav)
    difficulte = determiner_difficulte_cible(maitrise)
    
    with get_db_connection() as session:
        # On exclut ce qu'il a déjà réussi
        subquery = session.query(TentativeExerciceModel.id_exercice).filter(
            and_(
                TentativeExerciceModel.id_apprenant == id_apprenant,
                TentativeExerciceModel.score_obtenu >= 0.7
            )
        )
        
        exercices = session.query(ExerciceInstanceModel).filter(
            and_(
                ExerciceInstanceModel.id_aav_cible == id_aav,
                ExerciceInstanceModel.difficulte == difficulte,
                ~ExerciceInstanceModel.id_exercice.in_(subquery)
            )
        ).limit(nb_exercices).all()
        
        return [
            {
                "id_exercice": e.id_exercice,
                "titre": e.titre,
                "difficulte": e.difficulte,
                "type_evaluation": e.type_evaluation
            } for e in exercices
        ]
