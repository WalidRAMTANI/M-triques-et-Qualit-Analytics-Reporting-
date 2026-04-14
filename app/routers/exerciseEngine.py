# app/routeurs/exerciseEngine.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from app.models import (
    PromptFabricationAAV,
    RegleProgression,
    SelectionExercicesRequest,
    SequenceExercicesRequest,
    PreviewPromptRequest,
    EvaluationRequest,
)
from app.database import (
    get_db_connection, to_json, from_json
)
from app.services import (
    calculer_maitrise_reelle,
    determiner_difficulte_cible,
    selectionner_sequence_exercices,
)
from app.routeurs.promptFabricationAAV import PromptRepository


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
    """Récupère un AAV par son ID, retourne None s'il n'existe pas."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM aav WHERE id_aav = ?", (id_aav,))
        row = cursor.fetchone()
        return dict(row) if row else None


def _get_apprenant(id_apprenant: int) -> Optional[dict]:
    """Récupère un apprenant par son ID, retourne None s'il n'existe pas."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM apprenant WHERE id_apprenant = ?",
            (id_apprenant,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


# ============================================================
# GESTION PAR AAV
# ============================================================

@router.get("/aavs/{id_aav}/prompts", response_model=List[PromptFabricationAAV])
def get_prompts_for_aav(id_aav: int):
    """Liste tous les prompts actifs associés à un AAV donné."""
    if not _get_aav(id_aav):
        raise HTTPException(status_code=404, detail="AAV non trouvé")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM prompt_fabrication_aav
                WHERE cible_aav_id = ? AND is_active = 1
            """, (id_aav,))
            rows = cursor.fetchall()
        return [PromptFabricationAAV(**dict(row)) for row in rows]
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
    """
    if not _get_aav(id_aav):
        raise HTTPException(status_code=404, detail="AAV non trouvé")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*,
                       AVG(e.taux_succes_moyen) AS score_moyen,
                       COUNT(e.id_exercice)     AS nb_exercices
                FROM prompt_fabrication_aav p
                LEFT JOIN exercice_instance e
                    ON e.id_prompt_source = p.id_prompt
                WHERE p.cible_aav_id = ? AND p.is_active = 1
                GROUP BY p.id_prompt
                ORDER BY score_moyen DESC, nb_exercices DESC
                LIMIT 1
            """, (id_aav,))
            row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"Aucun prompt actif pour l'AAV {id_aav}"
            )
        return PromptFabricationAAV(**dict(row))
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


# ============================================================
# RÈGLES DE PROGRESSION
# ============================================================

@router.get("/progression-rules")
def list_progression_rules():
    """Retourne les règles de progression de tous les AAV actifs."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_aav, nom, discipline, regles_progression
                FROM aav
                WHERE is_active = 1 AND regles_progression IS NOT NULL
            """)
            rows = cursor.fetchall()
        return [
            {
                "id_aav": row["id_aav"],
                "nom": row["nom"],
                "discipline": row["discipline"],
                "regles_progression": from_json(row["regles_progression"])
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progression-rules/{id_aav}")
def get_progression_rules(id_aav: int):
    """Récupère les règles de progression d'un AAV spécifique."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_aav, nom, discipline, regles_progression"
                " FROM aav WHERE id_aav = ?",
                (id_aav,)
            )
            row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="AAV non trouvé")
        regles = from_json(row["regles_progression"])
        if not regles:
            raise HTTPException(
                status_code=404,
                detail=f"Aucune règle définie pour l'AAV {id_aav}"
            )
        return {
            "id_aav": row["id_aav"],
            "nom": row["nom"],
            "discipline": row["discipline"],
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
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_aav, nom FROM aav WHERE id_aav = ?", (id_aav,)
            )
            row = cursor.fetchone()
            if not row:
                raise HTTPException(
                    status_code=404, detail="AAV non trouvé"
                )
            cursor.execute(
                "UPDATE aav SET regles_progression = ?,"
                " updated_at = CURRENT_TIMESTAMP WHERE id_aav = ?",
                (to_json(regles.model_dump()), id_aav)
            )
        return {
            "id_aav": id_aav,
            "nom": row["nom"],
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
    id_apprenant: int = Depends(_get_apprenant)
):
    """Sélectionne intelligemment le prochain exercice pour un apprenant."""
    maitrise = calculer_maitrise_reelle(id_apprenant, id_aav)
    difficulte_cible = determiner_difficulte_cible(maitrise)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT e.* FROM exercice_instance e
            WHERE e.id_aav_cible = ?
              AND e.difficulte = ?
              AND e.id_exercice NOT IN (
                  SELECT id_exercice FROM tentative_exercice
                  WHERE id_apprenant = ? AND score_obtenu >= 0.7
              )
            ORDER BY e.taux_succes_moyen DESC
            LIMIT 1
        """
        cursor.execute(query, (id_aav, difficulte_cible, id_apprenant))
        exercice = cursor.fetchone()

        if not exercice:
            cursor.execute("""
                SELECT * FROM exercice_instance
                WHERE id_aav_cible = ? AND difficulte = ?
                ORDER BY taux_succes_moyen DESC LIMIT 1
            """, (id_aav, difficulte_cible))
            exercice = cursor.fetchone()

    if not exercice:
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
            "difficulte_cible": difficulte_cible
        },
        "exercice": dict(exercice)
    }


@router.get("/sequence/{id_apprenant}/{id_aav}")
def get_exercise_sequence(id_apprenant: int, id_aav: int, nb: int = 3):
    """Renvoie une liste d'exercices adaptés au niveau réel de l'élève."""
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
    Sélectionne les meilleurs exercices pour un apprenant.

    - adaptive   : exercices adaptés au niveau réel de chaque AAV (défaut)
    - random     : exercices tirés aléatoirement dans le pool disponible
    - progressive: exercices ordonnés du plus facile au plus difficile
    """
    if not _get_apprenant(body.id_apprenant):
        raise HTTPException(
            status_code=404,
            detail=f"Apprenant {body.id_apprenant} non trouvé"
        )

    exercices_selectionnes = []

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            for id_aav in body.id_aavs_cibles:
                if not _get_aav(id_aav):
                    continue

                if body.strategie == "random":
                    cursor.execute("""
                        SELECT * FROM exercice_instance
                        WHERE id_aav_cible = ?
                        ORDER BY RANDOM()
                        LIMIT ?
                    """, (id_aav, body.nombre_exercices))
                    rows = cursor.fetchall()
                    exercices_selectionnes.extend([dict(r) for r in rows])

                elif body.strategie == "progressive":
                    for niveau in ["debutant", "intermediaire", "avance"]:
                        cursor.execute("""
                            SELECT * FROM exercice_instance
                            WHERE id_aav_cible = ? AND difficulte = ?
                            ORDER BY taux_succes_moyen DESC
                            LIMIT ?
                        """, (id_aav, niveau, body.nombre_exercices))
                        rows = cursor.fetchall()
                        exercices_selectionnes.extend(
                            [dict(r) for r in rows]
                        )

                else:  # adaptive (défaut)
                    maitrise = calculer_maitrise_reelle(
                        body.id_apprenant, id_aav
                    )
                    difficulte = determiner_difficulte_cible(maitrise)
                    cursor.execute("""
                        SELECT * FROM exercice_instance
                        WHERE id_aav_cible = ? AND difficulte = ?
                          AND id_exercice NOT IN (
                              SELECT id_exercice FROM tentative_exercice
                              WHERE id_apprenant = ?
                                AND score_obtenu >= 0.7
                          )
                        ORDER BY taux_succes_moyen DESC
                        LIMIT ?
                    """, (
                        id_aav, difficulte,
                        body.id_apprenant, body.nombre_exercices
                    ))
                    rows = cursor.fetchall()
                    exercices_selectionnes.extend([dict(r) for r in rows])

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

    - Alterne les niveaux de difficulté pour varier
    - Priorise les types d'évaluation non récemment utilisés
    - Exclut les exercices déjà réussis
    """
    if not _get_apprenant(body.id_apprenant):
        raise HTTPException(
            status_code=404,
            detail=f"Apprenant {body.id_apprenant} non trouvé"
        )

    sequence = []
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DISTINCT e.type_evaluation
                FROM tentative_exercice t
                JOIN exercice_instance e ON t.id_exercice = e.id_exercice
                WHERE t.id_apprenant = ?
                ORDER BY t.date_tentative DESC
                LIMIT 10
            """, (body.id_apprenant,))
            types_recents = {
                r["type_evaluation"] for r in cursor.fetchall()
            }

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

                placeholders = (
                    ",".join("?" * len(types_recents))
                    if types_recents else "''"
                )
                params = (
                    [id_aav, difficulte_cible, body.id_apprenant]
                    + list(types_recents)
                )
                cursor.execute(f"""
                    SELECT * FROM exercice_instance
                    WHERE id_aav_cible = ? AND difficulte = ?
                      AND id_exercice NOT IN (
                          SELECT id_exercice FROM tentative_exercice
                          WHERE id_apprenant = ? AND score_obtenu >= 0.7
                      )
                    ORDER BY
                        CASE WHEN type_evaluation
                            NOT IN ({placeholders}) THEN 0 ELSE 1 END,
                        taux_succes_moyen DESC
                    LIMIT 1
                """, params)
                exercice = cursor.fetchone()

                if not exercice:
                    cursor.execute("""
                        SELECT * FROM exercice_instance
                        WHERE id_aav_cible = ? AND difficulte = ?
                        ORDER BY taux_succes_moyen DESC LIMIT 1
                    """, (id_aav, difficulte_base))
                    exercice = cursor.fetchone()

                if exercice:
                    sequence.append({
                        "ordre": len(sequence) + 1,
                        "id_aav": id_aav,
                        "maitrise_actuelle": maitrise,
                        "difficulte_cible": difficulte_cible,
                        "exercice": dict(exercice)
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
    Retourne le prompt enrichi avec le contexte de l'apprenant,
    prêt à être envoyé à une API LLM.
    """
    prompt_data = repo.get_by_id(id_prompt)
    if not prompt_data:
        raise HTTPException(status_code=404, detail="Prompt non trouvé")

    if not _get_apprenant(body.id_apprenant):
        raise HTTPException(
            status_code=404,
            detail=f"Apprenant {body.id_apprenant} non trouvé"
        )

    try:
        prompt_texte = prompt_data["prompt_texte"]
        id_aav = prompt_data["cible_aav_id"]

        if body.include_context:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id_aav_cible FROM statut_apprentissage
                    WHERE id_apprenant = ? AND est_maitrise = 1
                """, (body.id_apprenant,))
                aavs_maitrises = [
                    r["id_aav_cible"] for r in cursor.fetchall()
                ]

                cursor.execute("""
                    SELECT id_aav_cible, niveau_maitrise
                    FROM statut_apprentissage
                    WHERE id_apprenant = ?
                      AND est_maitrise = 0
                      AND niveau_maitrise > 0
                """, (body.id_apprenant,))
                aavs_en_cours = [
                    {"id_aav": r["id_aav_cible"], "niveau": r["niveau_maitrise"]}
                    for r in cursor.fetchall()
                ]

                cursor.execute(
                    "SELECT nom, description_markdown, type_evaluation"
                    " FROM aav WHERE id_aav = ?",
                    (id_aav,)
                )
                aav = cursor.fetchone()

            maitrise_actuelle = calculer_maitrise_reelle(
                body.id_apprenant, id_aav
            )
            difficulte = determiner_difficulte_cible(maitrise_actuelle)

            prompt_enrichi = (
                f"=== CONTEXTE APPRENANT (id: {body.id_apprenant}) ===\n"
                f"- Niveau de maîtrise sur cet AAV :"
                f" {maitrise_actuelle * 100:.0f}%\n"
                f"- Difficulté recommandée         : {difficulte}\n"
                f"- AAV déjà maîtrisés             :"
                f" {aavs_maitrises if aavs_maitrises else 'aucun'}\n"
                f"- AAV en cours d'apprentissage   :"
                f" {aavs_en_cours if aavs_en_cours else 'aucun'}\n\n"
                f"=== AAV CIBLE (id: {id_aav}) ===\n"
                f"- Nom          :"
                f" {aav['nom'] if aav else 'inconnu'}\n"
                f"- Description  :"
                f" {aav['description_markdown'] if aav else ''}\n"
                f"- Type éval.   :"
                f" {aav['type_evaluation'] if aav else ''}\n\n"
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
    Évalue la réponse d'un apprenant à un exercice et enregistre
    la tentative.

    - Calcul Automatisé : compare avec la solution dans le contenu JSON
    - Autres types      : score 0.5, évaluation humaine/pairs requise
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM exercice_instance WHERE id_exercice = ?",
            (body.id_exercice,)
        )
        exercice = cursor.fetchone()

    if not exercice:
        raise HTTPException(
            status_code=404,
            detail=f"Exercice {body.id_exercice} non trouvé"
        )

    try:
        exercice = dict(exercice)
        score = 0.0
        feedback = ""

        if body.type_evaluation == "Calcul Automatisé":
            contenu = from_json(exercice.get("contenu") or "{}")
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

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tentative_exercice
                    (id_exercice, reponse_donnee, score_obtenu,
                     feedback_genere, date_tentative)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                body.id_exercice,
                body.reponse_apprenant,
                score,
                feedback
            ))
            id_tentative = cursor.lastrowid

            cursor.execute("""
                UPDATE exercice_instance
                SET taux_succes_moyen = (
                        SELECT AVG(score_obtenu)
                        FROM tentative_exercice WHERE id_exercice = ?
                    ),
                    nb_utilisations = (
                        SELECT COUNT(*)
                        FROM tentative_exercice WHERE id_exercice = ?
                    )
                WHERE id_exercice = ?
            """, (
                body.id_exercice, body.id_exercice, body.id_exercice
            ))

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
    Retourne le taux de succès agrégé de tous les exercices
    générés à partir de ce prompt.
    """
    prompt_data = repo.get_by_id(id_prompt)
    if not prompt_data:
        raise HTTPException(status_code=404, detail="Prompt non trouvé")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    COUNT(e.id_exercice)    AS nb_exercices,
                    SUM(e.nb_utilisations)  AS nb_tentatives_total,
                    AVG(e.taux_succes_moyen) AS taux_succes_moyen,
                    MAX(e.taux_succes_moyen) AS meilleur_taux,
                    MIN(e.taux_succes_moyen) AS pire_taux
                FROM exercice_instance e
                WHERE e.id_prompt_source = ?
            """, (id_prompt,))
            stats = cursor.fetchone()

            cursor.execute("""
                SELECT id_exercice, titre, difficulte,
                       nb_utilisations, taux_succes_moyen
                FROM exercice_instance
                WHERE id_prompt_source = ?
                ORDER BY taux_succes_moyen DESC
            """, (id_prompt,))
            detail_exercices = [dict(r) for r in cursor.fetchall()]

        return {
            "id_prompt": id_prompt,
            "cible_aav_id": prompt_data["cible_aav_id"],
            "nb_exercices_generes": stats["nb_exercices"] or 0,
            "nb_tentatives_total": stats["nb_tentatives_total"] or 0,
            "taux_succes_moyen": round(
                stats["taux_succes_moyen"] or 0.0, 3
            ),
            "meilleur_taux": round(stats["meilleur_taux"] or 0.0, 3),
            "pire_taux": round(stats["pire_taux"] or 0.0, 3),
            "detail_exercices": detail_exercices
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
