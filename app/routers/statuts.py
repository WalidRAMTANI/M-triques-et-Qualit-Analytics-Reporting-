# app/routers/statuts.py

from fastapi import APIRouter, HTTPException # type: ignore
from typing import List, Optional
from app.database import (
    get_db_connection, from_json, to_json, 
    StatutApprentissageModel, TentativeModel
)
from app.model.model import (
    StatutApprentissage, StatutApprentissageCreate, 
    StatutApprentissageUpdate, StatutApprentissageMasteryUpdate, Tentative
)
from datetime import datetime
from sqlalchemy import and_


router = APIRouter(tags=["Statuts"])

# Helper functions are no longer needed as we use model_validate


@router.get("/learning-status", response_model=List[StatutApprentissage])
def get_learning_status(id_apprenant: Optional[int] = None, id_aav: Optional[int] = None):
    """
    Récupère la liste des statuts d'apprentissage, filtrable par apprenant ou AAV.

    Args:
        id_apprenant (Optional[int]): Filtrer par identifiant d'apprenant.
        id_aav (Optional[int]): Filtrer par identifiant d'AAV.

    Returns:
        List[StatutApprentissage]: Liste des statuts correspondants.
    """
    with get_db_connection() as session:
        query = session.query(StatutApprentissageModel)

        if id_apprenant is not None:
            query = query.filter(StatutApprentissageModel.id_apprenant == id_apprenant)

        if id_aav is not None:
            query = query.filter(StatutApprentissageModel.id_aav_cible == id_aav)

        results = query.all()
        return [StatutApprentissage.model_validate(r) for r in results]


@router.get("/learning-status/{statut_id}", response_model=StatutApprentissage)
def get_learning_status_by_id(statut_id: int):
    """
    Récupère un statut d'apprentissage spécifique par son identifiant unique.

    Args:
        statut_id (int): L'identifiant du statut d'apprentissage.

    Returns:
        StatutApprentissage: Les données du statut d'apprentissage.

    Raises:
        HTTPException: 404 si le statut n'est pas trouvé.
    """
    with get_db_connection() as session:
        res = session.query(StatutApprentissageModel).filter(StatutApprentissageModel.id == statut_id).first()

        if not res:
            raise HTTPException(status_code=404, detail=f"Statut d'apprentissage d'ID {statut_id} non trouvé")

        return StatutApprentissage.model_validate(res)


@router.post("/learning-status", response_model=StatutApprentissage, status_code=201)
def create_learning_status(statut: StatutApprentissageCreate):
    """
    Crée un nouveau statut d'apprentissage pour un couple apprenant/AAV.

    Args:
        statut (StatutApprentissageCreate): Les données de création du statut.

    Returns:
        StatutApprentissage: Le statut créé.

    Raises:
        HTTPException: 400 si le statut existe déjà.
    """
    with get_db_connection() as session:
        existe = session.query(StatutApprentissageModel).filter(
            and_(
                StatutApprentissageModel.id_apprenant == statut.id_apprenant,
                StatutApprentissageModel.id_aav_cible == statut.id_aav_cible
            )
        ).first()

        if existe:
            raise HTTPException(status_code=400, detail=f"Un statut d'apprentissage pour l'apprenant {statut.id_apprenant} et l'AAV {statut.id_aav_cible} existe déjà")

        new_status = StatutApprentissageModel(
            id_apprenant=statut.id_apprenant,
            id_aav_cible=statut.id_aav_cible,
            niveau_maitrise=statut.niveau_maitrise,
            historique_tentatives_ids=statut.historique_tentatives_ids,
            date_debut_apprentissage=datetime.now(),
            date_derniere_session=datetime.now()
        )
        session.add(new_status)
        session.commit()
        session.refresh(new_status)
        return StatutApprentissage.model_validate(new_status)


@router.put("/learning-status/{statut_id}", response_model=StatutApprentissage)
def update_learning_status(statut_id: int, statut: StatutApprentissageUpdate):
    """
    Met à jour un statut d'apprentissage déjà existant dans la base de données.

    Args:
        statut_id (int): L'ID du statut d'apprentissage à mettre à jour
        statut (StatutApprentissageUpdate): L'objet contenant les nouvelles données

    Raises:
        HTTPException: Si le statut d'apprentissage n'est pas trouvé (404)

    Returns:
        StatutApprentissage: Le statut d'apprentissage mis à jour
    """

    with get_db_connection() as session:
        obj = session.query(StatutApprentissageModel).filter(StatutApprentissageModel.id == statut_id).first()
        if not obj:
            raise HTTPException(status_code=404, detail=f"Statut d'apprentissage d'ID {statut_id} non trouvé")

        if statut.niveau_maitrise is not None:
            obj.niveau_maitrise = statut.niveau_maitrise
        
        if statut.historique_tentatives_ids is not None:
            obj.historique_tentatives_ids = statut.historique_tentatives_ids

        obj.date_derniere_session = datetime.now()
        session.commit()
        session.refresh(obj)
        return StatutApprentissage.model_validate(obj)


@router.patch("/learning-status/{statut_id}/mastery", response_model=StatutApprentissage)
def update_mastery(statut_id: int, statut: StatutApprentissageMasteryUpdate):
    """
    Met à jour uniquement le niveau de maîtrise d'un statut d'apprentissage.

    Args:
        statut_id (int): L'identifiant du statut.
        statut (StatutApprentissageMasteryUpdate): Le nouveau niveau de maîtrise.

    Returns:
        StatutApprentissage: Le statut mis à jour.

    Raises:
        HTTPException: 404 si le statut n'est pas trouvé.
    """
    with get_db_connection() as session:
        obj = session.query(StatutApprentissageModel).filter(StatutApprentissageModel.id == statut_id).first()
        if not obj:
            raise HTTPException(status_code=404, detail=f"Statut d'apprentissage d'ID {statut_id} non trouvé")
        
        obj.niveau_maitrise = statut.niveau_maitrise
        obj.date_derniere_session = datetime.now()
        session.commit()
        session.refresh(obj)
        return StatutApprentissage.model_validate(obj)


@router.get("/learning-status/{id}/attempts", response_model=List[Tentative])
def get_attempts_by_id(id: int):
    """
    Récupère l'historique des tentatives associées à un statut d'apprentissage.

    Args:
        id (int): L'identifiant du statut d'apprentissage.

    Returns:
        List[Tentative]: Liste des tentatives associées (ordre chronologique).

    Raises:
        HTTPException: 404 si le statut n'est pas trouvé.
    """
    with get_db_connection() as session:
        statut = session.query(StatutApprentissageModel).filter(StatutApprentissageModel.id == id).first()
        if not statut:
            raise HTTPException(status_code=404, detail=f"Statut d'apprentissage d'ID {id} non trouvé")

        res = session.query(TentativeModel).filter(
            and_(
                TentativeModel.id_apprenant == statut.id_apprenant,
                TentativeModel.id_aav_cible == statut.id_aav_cible
            )
        ).order_by(TentativeModel.date_tentative.asc()).all()

        return [Tentative.model_validate(r) for r in res]



@router.get("/learning-status/{id}/attempts/timeline", response_model=List[Tentative])
def get_attempts_timeline_by_id(id: int):
    """
    Récupère la timeline chronologique inverse des tentatives.

    Args:
        id (int): L'identifiant du statut d'apprentissage.

    Returns:
        List[Tentative]: Liste des tentatives de la plus récente à la plus ancienne.

    Raises:
        HTTPException: 404 si le statut n'est pas trouvé.
    """
    with get_db_connection() as session:
        statut = session.query(StatutApprentissageModel).filter(StatutApprentissageModel.id == id).first()
        if not statut:
            raise HTTPException(status_code=404, detail=f"Statut d'apprentissage d'ID {id} non trouvé")
        
        res = session.query(TentativeModel).filter(
            and_(
                TentativeModel.id_apprenant == statut.id_apprenant,
                TentativeModel.id_aav_cible == statut.id_aav_cible
            )
        ).order_by(TentativeModel.date_tentative.desc()).all()
    
        return [Tentative.model_validate(r) for r in res]


@router.post("/learning-status/{id}/reset", response_model=StatutApprentissage)
def reset_learning_status(id: int):
    """
    Réinitialise un statut d'apprentissage (maîtrise à 0 et historique vidé).

    Args:
        id (int): L'identifiant du statut d'apprentissage.

    Returns:
        StatutApprentissage: Le statut réinitialisé.

    Raises:
        HTTPException: 404 si le statut n'est pas trouvé.
    """
    with get_db_connection() as session:
        statut = session.query(StatutApprentissageModel).filter(StatutApprentissageModel.id == id).first()
        if not statut:
            raise HTTPException(status_code=404, detail=f"Statut d'apprentissage d'ID {id} non trouvé")
        
        statut.niveau_maitrise = 0.0
        statut.historique_tentatives_ids = []
        statut.date_derniere_session = datetime.now()
        session.commit()
        session.refresh(statut)
        return StatutApprentissage.model_validate(statut)


