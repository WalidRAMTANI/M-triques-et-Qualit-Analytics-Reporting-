# app/routeurs/exerciseEngine.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime

from app.model.model import (
    PromptFabricationAAV,
    RegleProgression,
    SelectionExercicesRequest,
    SequenceExercicesRequest,
    PreviewPromptRequest,
    EvaluationRequest,
)
from app.database import (
    get_db_connection, to_json, from_json,
    AAVModel, ApprenantModel, PromptFabricationAAVModel, ExerciceInstanceModel,
    TentativeExerciceModel
)
from sqlalchemy import and_, func, case

from app.services import (
    calculer_maitrise_reelle,
    determiner_difficulte_cible,
    selectionner_sequence_exercices,
)
from app.routers.promptFabricationAAV import PromptRepository


router = APIRouter(
    tags=["Exercise Engine"],
    responses={
        404: {"description": "Ressource non trouvée"},
        422: {"description": "Données invalides"},
        500: {"description": "Erreur serveur"},
    }
)


repo = PromptRepository()


# ============================================================
# FONCTIONS UTILITAIRES PRIVÉES
# ============================================================

def _get_aav(id_aav: int) -> Optional[dict]:
    """
    Récupère un AAV par son ID.

    Args:
        id_aav (int): L'identifiant unique de l'AAV.

    Returns:
        Optional[dict]: Un dictionnaire contenant les infos de l'AAV ou None si non trouvé.
    """
    with get_db_connection() as session:
        aav = session.query(AAVModel).filter(AAVModel.id_aav == id_aav).first()
        if not aav:
            return None
        return {
            "id_aav": aav.id_aav,
            "nom": aav.nom,
            "type_evaluation": aav.type_evaluation,
            "description_markdown": aav.description_markdown,
            "discipline": aav.discipline
        }


def _get_apprenant(id_apprenant: int) -> Optional[dict]:
    """
    Récupère un apprenant par son ID.

    Args:
        id_apprenant (int): L'identifiant unique de l'apprenant.

    Returns:
        Optional[dict]: Un dictionnaire avec les infos de l'apprenant ou None si non trouvé.
    """
    with get_db_connection() as session:
        apprenant = session.query(ApprenantModel).filter(ApprenantModel.id_apprenant == id_apprenant).first()
        if not apprenant:
            return None
        return {
            "id_apprenant": apprenant.id_apprenant,
            "nom_utilisateur": apprenant.nom_utilisateur
        }


# ============================================================
# GESTION PAR AAV
# ============================================================

@router.get("/aavs/{id_aav}/prompts", response_model=List[PromptFabricationAAV])
def get_prompts_for_aav(id_aav: int):
    """
    Liste tous les prompts actifs associés à un AAV donné.

    Args:
        id_aav (int): L'identifiant de l'AAV cible.

    Returns:
        List[PromptFabricationAAV]: La liste des prompts trouvés.

    Raises:
        HTTPException: 404 si l'AAV n'existe pas, 500 en cas d'erreur DB.
    """
    if not _get_aav(id_aav):
        raise HTTPException(status_code=404, detail="AAV non trouvé")
    try:
        with get_db_connection() as session:
            rows = session.query(PromptFabricationAAVModel).filter(
                and_(
                    PromptFabricationAAVModel.cible_aav_id == id_aav,
                    PromptFabricationAAVModel.is_active == True
                )
            ).all()
            return [PromptFabricationAAV.model_validate(r) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/aavs/{id_aav}/prompts/best",
    response_model=PromptFabricationAAV
)
def get_best_prompt_for_aav(id_aav: int):
    """
    Retourne le meilleur prompt pour un AAV selon le taux de succès
    moyen des exercices qu'il a générés.

    Args:
        id_aav (int): L'identifiant de l'AAV.

    Returns:
        PromptFabricationAAV: Les données du meilleur prompt.

    Raises:
        HTTPException: 404 si l'AAV n'existe pas ou n'a pas de prompt, 500 en cas d'erreur DB.
    """
    if not _get_aav(id_aav):
        raise HTTPException(status_code=404, detail="AAV non trouvé")
    try:
        with get_db_connection() as session:
            # Query joined with avg and count
            result = session.query(
                PromptFabricationAAVModel,
                func.avg(ExerciceInstanceModel.taux_succes_moyen).label("score_moyen"),
                func.count(ExerciceInstanceModel.id_exercice).label("nb_exercices")
            ).outerjoin(ExerciceInstanceModel, ExerciceInstanceModel.id_prompt_source == PromptFabricationAAVModel.id_prompt)\
             .filter(and_(
                 PromptFabricationAAVModel.cible_aav_id == id_aav,
                 PromptFabricationAAVModel.is_active == True
             ))\
             .group_by(PromptFabricationAAVModel.id_prompt)\
             .order_by(func.avg(ExerciceInstanceModel.taux_succes_moyen).desc(), 
                       func.count(ExerciceInstanceModel.id_exercice).desc())\
             .first()
             
            if not result or not result[0]:
                raise HTTPException(
                    status_code=404,
                    detail=f"Aucun prompt actif pour l'AAV {id_aav}"
                )
            return PromptFabricationAAV.model_validate(result[0])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/aavs/{id_aav}/prompts/generate",
    response_model=PromptFabricationAAV,
    status_code=201
)
def generate_prompt_for_aav(id_aav: int):
    """
    Génère automatiquement un nouveau prompt pour un AAV
    basé sur sa description et son type d'évaluation.

    Args:
        id_aav (int): L'identifiant de l'AAV.

    Returns:
        PromptFabricationAAV: Le nouveau prompt généré.

    Raises:
        HTTPException: 404 si l'AAV n'existe pas, 500 en cas d'erreur technique.
    """
    aav = _get_aav(id_aav)
    if not aav:
        raise HTTPException(status_code=404, detail="AAV non trouvé")
    try:
        type_eval = aav.get("type_evaluation", "Calcul Automatisé")
        nom_aav = aav.get("nom", "")
        description = aav.get("description_markdown", "")

        prompt_texte = (
            f"Génère un exercice de type '{type_eval}'"
            f" pour l'AAV suivant.\n"
            f"AAV : {nom_aav}\n"
            f"Description : {description}\n"
            f"L'exercice doit être adapté au niveau de l'apprenant "
            f"et respecter le type d'évaluation demandé."
        )
        data = {
            "cible_aav_id": id_aav,
            "type_exercice_genere": type_eval,
            "prompt_texte": prompt_texte,
            "version_prompt": 1,
            "is_active": True,
            "metadata": to_json({"source": "auto-generated"}),
        }
        new_id = repo.create(data)
        created = repo.get_by_id(new_id)
        return PromptFabricationAAV(**created)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/progression-rules")
def list_progression_rules():
    """
    Retourne les règles de progression de tous les AAV actifs.

    Returns:
        List[dict]: Liste de règles par AAV.

    Raises:
        HTTPException: 500 en cas d'erreur base de données.
    """
    try:
        with get_db_connection() as session:
            rows = session.query(AAVModel).filter(
                and_(
                    AAVModel.is_active == True,
                    AAVModel.regles_progression != None
                )
            ).all()
            
            return [
                {
                    "id_aav": r.id_aav,
                    "nom": r.nom,
                    "discipline": r.discipline,
                    "regles_progression": from_json(r.regles_progression) if isinstance(r.regles_progression, str) else r.regles_progression
                }
                for r in rows
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progression-rules/{id_aav}")
def get_progression_rules(id_aav: int):
    """
    Récupère les règles de progression d'un AAV spécifique.

    Args:
        id_aav (int): L'identifiant de l'AAV.

    Returns:
        dict: Les règles de progression de l'AAV.

    Raises:
        HTTPException: 404 si l'AAV ou ses règles ne sont pas trouvés.
    """
    try:
        with get_db_connection() as session:
            row = session.query(AAVModel).filter(AAVModel.id_aav == id_aav).first()
            if not row:
                raise HTTPException(status_code=404, detail="AAV non trouvé")
            
            regles = from_json(row.regles_progression) if isinstance(row.regles_progression, str) else row.regles_progression
            if not regles:
                raise HTTPException(
                    status_code=404,
                    detail=f"Aucune règle définie pour l'AAV {id_aav}"
                )
            return {
                "id_aav": row.id_aav,
                "nom": row.nom,
                "discipline": row.discipline,
                "regles_progression": regles
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/progression-rules/{id_aav}")
def update_progression_rules(id_aav: int, regles: RegleProgression):
    """
    Modifie les règles de progression d'un AAV.
    Valide les données via le modèle Pydantic RegleProgression.

    Args:
        id_aav (int): L'identifiant de l'AAV.
        regles (RegleProgression): Les nouvelles règles à appliquer.

    Returns:
        dict: Confirmation de la mise à jour.

    Raises:
        HTTPException: 404 si l'AAV n'existe pas, 500 en cas d'erreur DB.
    """
    try:
        with get_db_connection() as session:
            row = session.query(AAVModel).filter(AAVModel.id_aav == id_aav).first()
            if not row:
                raise HTTPException(
                    status_code=404, detail="AAV non trouvé"
                )
            
            row.regles_progression = regles.model_dump()
            row.updated_at = datetime.now()
            session.commit()
            
            return {
                "id_aav": id_aav,
                "nom": row.nom,
                "regles_progression": regles.model_dump(),
                "message": "Règles de progression mises à jour avec succès"
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/next-exercise/{id_aav}")
def get_next_exercise(
    id_aav: int,
    id_apprenant: int = 0,
):
    """
    Sélectionne intelligemment le prochain exercice pour un apprenant.

    Args:
        id_aav (int): L'identifiant de l'AAV cible.
        id_apprenant (int, query): L'identifiant de l'apprenant (optionnel, 0 = anonyme).

    Returns:
        dict: Le prochain exercice sélectionné avec ses métadonnées.

    Raises:
        HTTPException: 404 si aucun exercice n'est trouvé.
    """
    maitrise = calculer_maitrise_reelle(id_apprenant, id_aav)
    difficulte_cible = determiner_difficulte_cible(maitrise)

    exercice_data = None
    with get_db_connection() as session:
        # Sous-requête : exercices déjà réussis par l'apprenant
        subquery = session.query(TentativeExerciceModel.id_exercice).filter(
            and_(
                TentativeExerciceModel.id_apprenant == id_apprenant,
                TentativeExerciceModel.score_obtenu >= 0.7
            )
        )

        exercice = session.query(ExerciceInstanceModel).filter(
            and_(
                ExerciceInstanceModel.id_aav_cible == id_aav,
                ExerciceInstanceModel.difficulte == difficulte_cible,
                ~ExerciceInstanceModel.id_exercice.in_(subquery)
            )
        ).order_by(ExerciceInstanceModel.taux_succes_moyen.desc()).first()

        if not exercice:
            exercice = session.query(ExerciceInstanceModel).filter(
                and_(
                    ExerciceInstanceModel.id_aav_cible == id_aav,
                    ExerciceInstanceModel.difficulte == difficulte_cible
                )
            ).order_by(ExerciceInstanceModel.taux_succes_moyen.desc()).first()

        # Extraire les données DANS la session pour éviter le "not bound to a Session"
        if exercice:
            exercice_data = {
                "id_exercice": exercice.id_exercice,
                "titre": exercice.titre,
                "contenu": from_json(exercice.contenu) if isinstance(exercice.contenu, str) else exercice.contenu,
                "difficulte": exercice.difficulte,
                "type_evaluation": exercice.type_evaluation,
            }

    if not exercice_data:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Aucun exercice trouvé pour l'AAV {id_aav}"
                f" au niveau {difficulte_cible}"
            )
        )

    return {
        "metadata": {
            "apprenant_id": id_apprenant,
            "maitrise_calculee": maitrise,
            "difficulte_cible": difficulte_cible,
        },
        "exercice": exercice_data,
    }


@router.get("/sequence/{id_apprenant}/{id_aav}")
def get_exercise_sequence(id_apprenant: int, id_aav: int, nb: int = 3):
    """
    Renvoie une liste d'exercices adaptés au niveau réel de l'élève.

    Args:
        id_apprenant (int): L'identifiant de l'apprenant.
        id_aav (int): L'identifiant de l'AAV cible.
        nb (int, optional): Nombre d'exercices souhaités. Par défaut 3.

    Returns:
        dict: Une séquence d'exercices.

    Raises:
        HTTPException: 404 si aucun exercice n'est disponible.
    """
    exercices = selectionner_sequence_exercices(
        id_apprenant, id_aav, nb_exercices=nb
    )

    if not exercices:
        raise HTTPException(
            status_code=404,
            detail="Aucun exercice disponible pour cet AAV."
        )

    return {
        "id_apprenant": id_apprenant,
        "id_aav": id_aav,
        "nb_exercices": len(exercices),
        "exercices": exercices
    }


# ============================================================
# POST /exercises/select
# ============================================================

@router.post("/exercises/select")
def select_exercises(body: SelectionExercicesRequest):
    """
    Sélectionne les meilleurs exercices pour un apprenant selon une stratégie donnée.

    Args:
        body (SelectionExercicesRequest): Les paramètres de sélection 
            (id_apprenant, id_aavs_cibles, strategie, nombre_exercices).

    Returns:
        List[dict]: La liste d'exercices sélectionnés.

    Raises:
        HTTPException: 404 si l'apprenant n'est pas trouvé.
    """
    if not _get_apprenant(body.id_apprenant):
        raise HTTPException(
            status_code=404,
            detail=f"Apprenant {body.id_apprenant} non trouvé"
        )

    exercices_selectionnes = []

    try:
        with get_db_connection() as session:
            for id_aav in body.id_aavs_cibles:
                if not _get_aav(id_aav):
                    continue

                if body.strategie == "random":
                    rows = session.query(ExerciceInstanceModel).filter(
                        ExerciceInstanceModel.id_aav_cible == id_aav
                    ).order_by(func.random()).limit(body.nombre_exercices).all()
                    exercices_selectionnes.extend([
                        {
                            "id_exercice": r.id_exercice,
                            "titre": r.titre,
                            "id_aav_cible": r.id_aav_cible,
                            "difficulte": r.difficulte,
                            "type_evaluation": r.type_evaluation
                        } for r in rows
                    ])

                elif body.strategie == "progressive":
                    for niveau in ["debutant", "intermediaire", "avance"]:
                        rows = session.query(ExerciceInstanceModel).filter(
                            and_(
                                ExerciceInstanceModel.id_aav_cible == id_aav,
                                ExerciceInstanceModel.difficulte == niveau
                            )
                        ).order_by(ExerciceInstanceModel.taux_succes_moyen.desc()).limit(body.nombre_exercices).all()
                        exercices_selectionnes.extend([
                            {
                                "id_exercice": r.id_exercice,
                                "titre": r.titre,
                                "id_aav_cible": r.id_aav_cible,
                                "difficulte": r.difficulte,
                                "type_evaluation": r.type_evaluation
                            } for r in rows
                        ])

                else:  # adaptive (défaut)
                    maitrise = calculer_maitrise_reelle(
                        body.id_apprenant, id_aav
                    )
                    difficulte = determiner_difficulte_cible(maitrise)
                    
                    subquery = session.query(TentativeExerciceModel.id_exercice).filter(
                        and_(
                            TentativeExerciceModel.id_apprenant == body.id_apprenant,
                            TentativeExerciceModel.score_obtenu >= 0.7
                        )
                    )
                    
                    rows = session.query(ExerciceInstanceModel).filter(
                        and_(
                            ExerciceInstanceModel.id_aav_cible == id_aav,
                            ExerciceInstanceModel.difficulte == difficulte,
                            ~ExerciceInstanceModel.id_exercice.in_(subquery)
                        )
                    ).order_by(ExerciceInstanceModel.taux_succes_moyen.desc()).limit(body.nombre_exercices).all()
                    
                    exercices_selectionnes.extend([
                        {
                            "id_exercice": r.id_exercice,
                            "titre": r.titre,
                            "id_aav_cible": r.id_aav_cible,
                            "difficulte": r.difficulte,
                            "type_evaluation": r.type_evaluation
                        } for r in rows
                    ])

        exercices_selectionnes = exercices_selectionnes[:body.nombre_exercices]

        return {
            "id_apprenant": body.id_apprenant,
            "strategie": body.strategie,
            "nombre_demande": body.nombre_exercices,
            "nombre_trouve": len(exercices_selectionnes),
            "exercices": exercices_selectionnes
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# POST /exercises/sequence
# ============================================================

@router.post("/exercises/sequence")
def generate_sequence(body: SequenceExercicesRequest):
    """
    Génère une séquence optimale d'exercices pour un apprenant.

    Args:
        body (SequenceExercicesRequest): Paramètres de la séquence 
            (id_apprenant, id_aavs_cibles, nombre_exercices).

    Returns:
        dict: La séquence d'exercices générée.

    Raises:
        HTTPException: 404 si l'apprenant n'est pas trouvé, 500 en cas d'erreur technique.
    """
    if not _get_apprenant(body.id_apprenant):
        raise HTTPException(
            status_code=404,
            detail=f"Apprenant {body.id_apprenant} non trouvé"
        )

    sequence = []
    try:
        with get_db_connection() as session:
            # Get recent evaluation types
            recent_rows = session.query(ExerciceInstanceModel.type_evaluation)\
                .join(TentativeExerciceModel, TentativeExerciceModel.id_exercice == ExerciceInstanceModel.id_exercice)\
                .filter(TentativeExerciceModel.id_apprenant == body.id_apprenant)\
                .order_by(TentativeExerciceModel.date_tentative.desc())\
                .limit(10).all()
            
            types_recents = {r[0] for r in recent_rows}

            niveaux_alternes = ["debutant", "intermediaire", "avance"]
            idx_niveau = 0

            for id_aav in body.id_aavs_cibles:
                if not _get_aav(id_aav):
                    continue

                maitrise = calculer_maitrise_reelle(
                    body.id_apprenant, id_aav
                )
                difficulte_base = determiner_difficulte_cible(maitrise)
                difficulte_cible = niveaux_alternes[idx_niveau % 3]
                idx_niveau += 1

                # Subquery for already succeeded exercises
                subquery = session.query(TentativeExerciceModel.id_exercice).filter(
                    and_(
                        TentativeExerciceModel.id_apprenant == body.id_apprenant,
                        TentativeExerciceModel.score_obtenu >= 0.7
                    )
                )

                exercice = session.query(ExerciceInstanceModel).filter(

                    and_(
                        ExerciceInstanceModel.id_aav_cible == id_aav,
                        ExerciceInstanceModel.difficulte == difficulte_cible,
                        ~ExerciceInstanceModel.id_exercice.in_(subquery)
                    )
                ).order_by(
                    case((ExerciceInstanceModel.type_evaluation.in_(types_recents), 1), else_=0),
                    ExerciceInstanceModel.taux_succes_moyen.desc()
                ).first()

                if not exercice:
                    exercice = session.query(ExerciceInstanceModel).filter(
                        and_(
                            ExerciceInstanceModel.id_aav_cible == id_aav,
                            ExerciceInstanceModel.difficulte == difficulte_base
                        )
                    ).order_by(ExerciceInstanceModel.taux_succes_moyen.desc()).first()

                if exercice:
                    sequence.append({
                        "ordre": len(sequence) + 1,
                        "id_aav": id_aav,
                        "maitrise_actuelle": maitrise,
                        "difficulte_cible": difficulte_cible,
                        "exercice": {
                            "id_exercice": exercice.id_exercice,
                            "titre": exercice.titre,
                            "id_aav_cible": exercice.id_aav_cible,
                            "difficulte": exercice.difficulte,
                            "type_evaluation": exercice.type_evaluation
                        }
                    })

                if len(sequence) >= body.nombre_exercices:
                    break

        return {
            "id_apprenant": body.id_apprenant,
            "nombre_exercices": len(sequence),
            "sequence": sequence
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# POST /prompts/{id_prompt}/preview
# ============================================================

@router.post("/prompts/{id_prompt}/preview")
def preview_prompt(id_prompt: int, body: PreviewPromptRequest):
    """
    Retourne le prompt enrichi avec le contexte de l'apprenant.
    Prépare le texte final prêt à être envoyé à une API LLM.

    Args:
        id_prompt (int): L'identifiant du prompt.
        body (PreviewPromptRequest): Paramètres (id_apprenant, include_context).

    Returns:
        dict: Le prompt enrichi et les infos de contexte.

    Raises:
        HTTPException: 404 si prompt ou apprenant non trouvé, 500 en cas d'erreur.
    """
    with get_db_connection() as session:
        prompt_obj = session.query(PromptFabricationAAVModel).filter(PromptFabricationAAVModel.id_prompt == id_prompt).first()
        if not prompt_obj:
            raise HTTPException(status_code=404, detail="Prompt non trouvé")
        
        prompt_data = PromptFabricationAAV.model_validate(prompt_obj).model_dump()

    if not _get_apprenant(body.id_apprenant):
        raise HTTPException(
            status_code=404,
            detail=f"Apprenant {body.id_apprenant} non trouvé"
        )

    try:
        prompt_texte = prompt_data["prompt_texte"]
        id_aav = prompt_data["cible_aav_id"]

        if body.include_context:
            from app.database import StatutApprentissageModel
            with get_db_connection() as session:
                rows_maitrises = session.query(StatutApprentissageModel.id_aav_cible)\
                    .filter(and_(StatutApprentissageModel.id_apprenant == body.id_apprenant, StatutApprentissageModel.est_maitrise == True)).all()
                aavs_maitrises = [r[0] for r in rows_maitrises]

                rows_en_cours = session.query(StatutApprentissageModel.id_aav_cible, StatutApprentissageModel.niveau_maitrise)\
                    .filter(and_(
                        StatutApprentissageModel.id_apprenant == body.id_apprenant,
                        StatutApprentissageModel.est_maitrise == False,
                        StatutApprentissageModel.niveau_maitrise > 0
                    )).all()
                aavs_en_cours = [
                    {"id_aav": r[0], "niveau": r[1]}
                    for r in rows_en_cours
                ]

                aav_obj = session.query(AAVModel).filter(AAVModel.id_aav == id_aav).first()
                # Extraire les valeurs DANS la session pour éviter le "not bound to a Session"
                aav_nom = aav_obj.nom if aav_obj else "inconnu"
                aav_desc = aav_obj.description_markdown if aav_obj else ""
                aav_type = aav_obj.type_evaluation if aav_obj else ""

            maitrise_actuelle = calculer_maitrise_reelle(
                body.id_apprenant, id_aav
            )
            difficulte = determiner_difficulte_cible(maitrise_actuelle)

            prompt_enrichi = (
                f"=== CONTEXTE APPRENANT (id: {body.id_apprenant}) ===\n"
                f"- Niveau de maîtrise sur cet AAV : {maitrise_actuelle * 100:.0f}%\n"
                f"- Difficulté recommandée         : {difficulte}\n"
                f"- AAV déjà maîtrisés             : {aavs_maitrises if aavs_maitrises else 'aucun'}\n"
                f"- AAV en cours d'apprentissage   : {aavs_en_cours if aavs_en_cours else 'aucun'}\n\n"
                f"=== AAV CIBLE (id: {id_aav}) ===\n"
                f"- Nom          : {aav_nom}\n"
                f"- Description  : {aav_desc}\n"
                f"- Type éval.   : {aav_type}\n\n"
                f"=== PROMPT DE GÉNÉRATION ===\n"
                f"{prompt_texte}"
            )
        else:
            prompt_enrichi = prompt_texte
            difficulte = determiner_difficulte_cible(
                calculer_maitrise_reelle(body.id_apprenant, id_aav)
            )

        return {
            "id_prompt": id_prompt,
            "id_apprenant": body.id_apprenant,
            "include_context": body.include_context,
            "difficulte_adaptee": difficulte,
            "prompt_enrichi": prompt_enrichi
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ============================================================
# POST /exercises/evaluate
# ============================================================

@router.post("/exercises/evaluate")
def evaluate_exercise(body: EvaluationRequest):
    """
    Évalue la réponse d'un apprenant à un exercice et enregistre la tentative.

    Args:
        body (EvaluationRequest): Données de l'exercice et réponse de l'apprenant.

    Returns:
        dict: Résultat de l'évaluation (score, feedback, succès).

    Raises:
        HTTPException: 404 si l'exercice n'est pas trouvé, 500 en cas d'erreur.
    """
    with get_db_connection() as session:
        exercice = session.query(ExerciceInstanceModel).filter(ExerciceInstanceModel.id_exercice == body.id_exercice).first()

        if not exercice:
            raise HTTPException(
                status_code=404,
                detail=f"Exercice {body.id_exercice} non trouvé"
            )

        try:
            score = 0.0
            feedback = ""

            if body.type_evaluation == "Calcul Automatisé":
                contenu = from_json(exercice.contenu or "{}")
                solution_attendue = (
                    str(contenu.get("solution", "")).strip().lower()
                )
                reponse = body.reponse_apprenant.strip().lower()

                if solution_attendue and reponse == solution_attendue:
                    score = 1.0
                    feedback = "Bonne réponse ! Félicitations."
                elif solution_attendue:
                    score = 0.0
                    feedback = (
                        f"Réponse incorrecte. La solution attendue était : "
                        f"{contenu.get('solution', 'non disponible')}"
                    )
                else:
                    score = 0.5
                    feedback = (
                        "Réponse enregistrée. Aucune solution automatique"
                        " disponible pour cet exercice."
                    )
            else:
                score = 0.5
                feedback = (
                    f"Réponse enregistrée pour une évaluation de type"
                    f" '{body.type_evaluation}'. "
                    f"Elle sera examinée manuellement ou soumise aux pairs."
                )

            # Insert new attempt
            new_tentative = TentativeExerciceModel(
                id_exercice=body.id_exercice,
                reponse_donnee=body.reponse_apprenant,
                score_obtenu=score,
                feedback_genere=feedback,
                date_tentative=datetime.now()
            )
            session.add(new_tentative)
            session.flush() # Get id_tentative
            id_tentative = new_tentative.id_tentative

            # Update exercise stats
            # We recalculate avg score and count
            stats = session.query(
                func.avg(TentativeExerciceModel.score_obtenu),
                func.count(TentativeExerciceModel.id_tentative)
            ).filter(TentativeExerciceModel.id_exercice == body.id_exercice).first()
            
            exercice.taux_succes_moyen = stats[0] or 0.0
            exercice.nb_utilisations = stats[1] or 0
            
            session.commit()

            return {
                "id_tentative": id_tentative,
                "id_exercice": body.id_exercice,
                "type_evaluation": body.type_evaluation,
                "score_obtenu": score,
                "feedback": feedback,
                "est_reussi": score >= 0.7
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# GET /prompts/{id_prompt}/success-rate
# ============================================================

@router.get("/prompts/{id_prompt}/success-rate")
def get_prompt_success_rate(id_prompt: int):
    """
    Retourne le taux de succès agrégé de tous les exercices générés à partir de ce prompt.

    Args:
        id_prompt (int): L'identifiant du prompt.

    Returns:
        dict: Statistiques de succès du prompt.

    Raises:
        HTTPException: 404 si le prompt n'existe pas.
    """
    with get_db_connection() as session:
        prompt_obj = session.query(PromptFabricationAAVModel).filter(PromptFabricationAAVModel.id_prompt == id_prompt).first()
        if not prompt_obj:
            raise HTTPException(status_code=404, detail="Prompt non trouvé")

        try:
            stats = session.query(
                func.count(ExerciceInstanceModel.id_exercice).label("nb_exercices"),
                func.sum(ExerciceInstanceModel.nb_utilisations).label("nb_tentatives_total"),
                func.avg(ExerciceInstanceModel.taux_succes_moyen).label("taux_succes_moyen"),
                func.max(ExerciceInstanceModel.taux_succes_moyen).label("meilleur_taux"),
                func.min(ExerciceInstanceModel.taux_succes_moyen).label("pire_taux")
            ).filter(ExerciceInstanceModel.id_prompt_source == id_prompt).first()

            detail_exercices_rows = session.query(
                ExerciceInstanceModel.id_exercice,
                ExerciceInstanceModel.titre,
                ExerciceInstanceModel.difficulte,
                ExerciceInstanceModel.nb_utilisations,
                ExerciceInstanceModel.taux_succes_moyen
            ).filter(ExerciceInstanceModel.id_prompt_source == id_prompt)\
             .order_by(ExerciceInstanceModel.taux_succes_moyen.desc()).all()
            
            detail_exercices = [
                {
                    "id_exercice": r.id_exercice,
                    "titre": r.titre,
                    "difficulte": r.difficulte,
                    "nb_utilisations": r.nb_utilisations,
                    "taux_succes_moyen": r.taux_succes_moyen
                }
                for r in detail_exercices_rows
            ]

            return {
                "id_prompt": id_prompt,
                "cible_aav_id": prompt_obj.cible_aav_id,
                "nb_exercices_generes": stats.nb_exercices or 0,
                "nb_tentatives_total": stats.nb_tentatives_total or 0,
                "taux_succes_moyen": round(stats.taux_succes_moyen or 0.0, 3),
                "meilleur_taux": round(stats.meilleur_taux or 0.0, 3),
                "pire_taux": round(stats.pire_taux or 0.0, 3),
                "detail_exercices": detail_exercices
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

