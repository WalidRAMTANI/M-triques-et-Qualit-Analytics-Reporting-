from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from app.database import (
    get_db_connection, from_json, to_json,
    TentativeModel, StatutApprentissageModel
)
from app.model.model import Tentative, TentativeCreate
from app.services.maitrise import calculer_maitrise, message
from app.model.model import Process
from sqlalchemy import and_


router = APIRouter(tags=["Tentatives"])


# row_to_tentative is no longer needed



@router.get("/attempts", response_model=List[Tentative])
def list_attempts(
    id_apprenant: Optional[int] = None,
    id_aav_cible: Optional[int] = None,
    est_valide: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
):
    """
    Récupère une liste de tentatives filtrables.

    Args:
        id_apprenant (Optional[int]): Filtrer par identifiant d'apprenant.
        id_aav_cible (Optional[int]): Filtrer par identifiant d'AAV.
        est_valide (Optional[bool]): Filtrer par validité de la tentative.
        limit (int): Nombre maximum de résultats à retourner (défaut 100).
        offset (int): Nombre de résultats à sauter (défaut 0).

    Returns:
        List[Tentative]: Liste des tentatives correspondant aux filtres.
    """
    with get_db_connection() as session:
        query = session.query(TentativeModel)

        if id_apprenant is not None:
            query = query.filter(TentativeModel.id_apprenant == id_apprenant)

        if id_aav_cible is not None:
            query = query.filter(TentativeModel.id_aav_cible == id_aav_cible)

        if est_valide is not None:
            query = query.filter(TentativeModel.est_valide == est_valide)

        results = query.order_by(TentativeModel.date_tentative.desc()).offset(offset).limit(limit).all()
        return [Tentative.model_validate(r) for r in results]



@router.get("/attempts/{id}", response_model=Tentative)
def get_attempt(id: int):
    """
    Récupère une tentative spécifique par son identifiant unique.

    Args:
        id (int): L'identifiant de la tentative.

    Returns:
        Tentative: Les données de la tentative.

    Raises:
        HTTPException: 404 si la tentative n'existe pas.
    """
    with get_db_connection() as session:
        obj = session.query(TentativeModel).filter(TentativeModel.id == id).first()
        if obj is None:
            raise HTTPException(status_code=404, detail=f"Tentative introuvable: id={id}")
        return Tentative.model_validate(obj)



@router.post("/attempts", response_model=Tentative, status_code=201)
def create_attempt(payload: TentativeCreate):
    """
    Crée une nouvelle tentative et met à jour le statut d'apprentissage associé.
    L'historique des tentatives et le niveau de maîtrise de l'apprenant sur l'AAV sont recalculés.

    Args:
        payload (TentativeCreate): Les données de la nouvelle tentative.

    Returns:
        Tentative: La tentative créée avec son identifiant.
    """
    with get_db_connection() as session:
        new_attempt = TentativeModel(
            id_exercice_ou_evenement=payload.id_exercice_ou_evenement,
            id_apprenant=payload.id_apprenant,
            id_aav_cible=payload.id_aav_cible,
            score_obtenu=payload.score_obtenu,
            est_valide=payload.est_valide,
            temps_resolution_secondes=payload.temps_resolution_secondes,
            meta_data=payload.meta_data
        )
        session.add(new_attempt)
        session.flush()
        new_id = new_attempt.id

        # Update StatutApprentissage
        statut = session.query(StatutApprentissageModel).filter(
            and_(
                StatutApprentissageModel.id_apprenant == payload.id_apprenant,
                StatutApprentissageModel.id_aav_cible == payload.id_aav_cible
            )
        ).first()

        if not statut:
            statut = StatutApprentissageModel(
                id_apprenant=payload.id_apprenant,
                id_aav_cible=payload.id_aav_cible,
                niveau_maitrise=0.0,
                historique_tentatives_ids=[],
                date_debut_apprentissage=datetime.now()
            )
            session.add(statut)
            session.flush()

        liste_hist = list(statut.historique_tentatives_ids or [])
        liste_hist.append(new_id)
        statut.historique_tentatives_ids = liste_hist
        statut.date_derniere_session = datetime.now()

        # Calcul mastery
        all_attempts = session.query(TentativeModel).filter(
            TentativeModel.id.in_(liste_hist)
        ).all()
        scores = [a.score_obtenu for a in all_attempts]
        
        ancien_niveau = statut.niveau_maitrise
        statut.niveau_maitrise = calculer_maitrise(scores, 0.8, 3) 
        session.commit()
        session.refresh(new_attempt)
        return Tentative.model_validate(new_attempt)


@router.delete("/attempts/{id}", status_code=204)
def delete_attempt(id: int):
    """
    Supprime une tentative de la base de données.

    Args:
        id (int): L'identifiant de la tentative à supprimer.

    Raises:
        HTTPException: 404 si la tentative n'existe pas.
    """
    with get_db_connection() as session:
        obj = session.query(TentativeModel).filter(TentativeModel.id == id).first()
        if obj is None:
            raise HTTPException(status_code=404, detail=f"Tentative introuvable: id={id}")
        session.delete(obj)
        session.commit()
    return None

@router.post("/attempts/{id}/process", response_model=Process)
def process_attempt(id: int):
    """
    Traite une tentative existante pour recalculer la progression de l'élève.
    Cette fonction met à jour le niveau de maîtrise réelle et le statut 'est_maitrise' 
    dans la table statut_apprentissage.

    Args:
        id (int): L'identifiant de la tentative à traiter.

    Returns:
        Process: Résumé du traitement effectué (ancien/nouveau niveau, message).

    Raises:
        HTTPException: 404 si la tentative n'est pas trouvée.
    """
    SEUIL_SUCCES = 0.9
    N_SUCCES_CONSEC = 5

    with get_db_connection() as session:
        # 1) Récupérer la tentative
        attempt = session.query(TentativeModel).filter(TentativeModel.id == id).first()
        if attempt is None:
            raise HTTPException(status_code=404, detail=f"Tentative introuvable: id={id}")

        id_apprenant = attempt.id_apprenant
        id_aav_cible = attempt.id_aav_cible

        # 2) Charger ou créer le statut
        statut = session.query(StatutApprentissageModel).filter(
            and_(
                StatutApprentissageModel.id_apprenant == id_apprenant,
                StatutApprentissageModel.id_aav_cible == id_aav_cible
            )
        ).first()

        if statut is None:
            statut = StatutApprentissageModel(
                id_apprenant=id_apprenant,
                id_aav_cible=id_aav_cible,
                niveau_maitrise=0.0,
                historique_tentatives_ids=[],
                date_debut_apprentissage=datetime.now()
            )
            session.add(statut)
            session.flush()

        ancien_niveau = float(statut.niveau_maitrise or 0.0)

        # 3) Mettre à jour l'historique (IDs des tentatives)
        hist = list(statut.historique_tentatives_ids or [])
        if id not in hist:
            hist.append(id)
            statut.historique_tentatives_ids = hist

        # 4) Récupérer tous les scores (dans l'ordre chronologique)
        all_attempts = session.query(TentativeModel).filter(
            and_(
                TentativeModel.id_apprenant == id_apprenant,
                TentativeModel.id_aav_cible == id_aav_cible
            )
        ).order_by(TentativeModel.date_tentative.asc(), TentativeModel.id.asc()).all()
        
        scores = [float(t.score_obtenu) for t in all_attempts]

        # 5) Calcul + message
        nouveau_niveau = calculer_maitrise(scores, SEUIL_SUCCES, N_SUCCES_CONSEC)
        est_maitrise = (nouveau_niveau >= 1.0)
        msg = message(ancien_niveau, nouveau_niveau, est_maitrise, N_SUCCES_CONSEC)

        # 6) Update statut
        statut.niveau_maitrise = nouveau_niveau
        statut.est_maitrise = est_maitrise
        statut.date_derniere_session = datetime.now()
        
        session.commit()

    # 7) Réponse
    return Process(
        tentative_id=id,
        id_apprenant=id_apprenant,
        id_aav_cible=id_aav_cible,
        ancien_niveau=ancien_niveau,
        nouveau_niveau=nouveau_niveau,
        est_maitrise=est_maitrise,
        message=msg,
    )
