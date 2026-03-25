# app/routers/activitePedagogique_sqlalchemy.py
"""
Router for Pedagogical Activities (Group 4) using SQLAlchemy ORM.

This module provides RESTful API endpoints for managing pedagogical activities,
including activity CRUD operations, exercise management, and learner session tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from app.database import SessionLocal, ActivitePedagogiqueModel, ExerciceInstanceModel, TentativeModel, SessionApprenantModel, AAVModel, ApprenantModel, get_db, from_json, to_json
import json
from datetime import datetime

router = APIRouter(prefix="/activites", tags=["Activities"])

@router.get("/types")
def get_activity_types(db: Session = Depends(get_db)):
    """
    Retrieve available activity types.
    
    Args:
        db (Session): Database session provided by dependency injection.
    
    Returns:
        dict: Dictionary containing list of available activity types 
              (pilotee, prof_definie, revision).
    """
    return {
        "types": [
            "pilotee",
            "prof_definie", 
            "revision"
        ]
    }


@router.get("/")
def list_activities(db: Session = Depends(get_db)):
    """
    Retrieve all pedagogical activities.
    
    Args:
        db (Session): Database session provided by dependency injection.
    
    Returns:
        list: List of activity dictionaries with basic information.
    """
    # get all activities from database
    activities = db.query(ActivitePedagogiqueModel).all()
    
    return [
        {
            "id_activite": a.id_activite,
            "nom": a.nom,
            "description": a.description,
            "type_activite": a.type_activite,
            "discipline": a.discipline,
            "niveau_difficulte": a.niveau_difficulte,
        }
        for a in activities
    ]


@router.get("/{activity_id}")
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    """
    Retrieve detailed information about a specific activity.
    
    Args:
        activity_id (int): The unique identifier of the activity.
        db (Session): Database session provided by dependency injection.
    
    Returns:
        dict: Activity dictionary with all fields including exercises list.
    
    Raises:
        HTTPException: 404 error if activity is not found.
    """
    # Retrieve activity by ID
    activity = db.query(ActivitePedagogiqueModel).filter(
        ActivitePedagogiqueModel.id_activite == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    return {
        "id_activite": activity.id_activite,
        "nom": activity.nom,
        "description": activity.description,
        "type_activite": activity.type_activite,
        "ids_exercices_inclus": from_json(activity.ids_exercices_inclus),
        "discipline": activity.discipline,
        "niveau_difficulte": activity.niveau_difficulte,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_activity(activity_data: dict, db: Session = Depends(get_db)):
    """
    Create a new pedagogical activity.
    
    Args:
        activity_data (dict): Dictionary containing activity fields.
        db (Session): Database session provided by dependency injection.
    
    Returns:
        dict: Dictionary with id_activite, nom, and success message.
    """
    # convert exercise list to JSON format before saving
    activity_data["ids_exercices_inclus"] = to_json(activity_data.get("ids_exercices_inclus", []))
    
    # Convert created_at string to datetime if it's a string
    if "created_at" in activity_data and isinstance(activity_data["created_at"], str):
        activity_data["created_at"] = datetime.fromisoformat(activity_data["created_at"].replace(" ", "T"))
    
    db_activity = ActivitePedagogiqueModel(**activity_data)
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    
    return {
        "id_activite": db_activity.id_activite,
        "nom": db_activity.nom,
        "message": "Activity created"
    }


@router.put("/{activity_id}")
def update_activity(activity_id: int, activity_data: dict, db: Session = Depends(get_db)):
    """
    Update an existing pedagogical activity.
    
    Args:
        activity_id (int): The unique identifier of the activity to update.
        activity_data (dict): Dictionary containing fields to update.
        db (Session): Database session provided by dependency injection.
    
    Returns:
        dict: Dictionary with success message.
    
    Raises:
        HTTPException: 404 error if activity is not found.
    """
    # Trouver l'activité et mettre à jour ses champs
    activity = db.query(ActivitePedagogiqueModel).filter(
        ActivitePedagogiqueModel.id_activite == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    if "ids_exercices_inclus" in activity_data:
        activity_data["ids_exercices_inclus"] = to_json(activity_data["ids_exercices_inclus"])
    
    # Convert created_at string to datetime if it's a string
    if "created_at" in activity_data and isinstance(activity_data["created_at"], str):
        activity_data["created_at"] = datetime.fromisoformat(activity_data["created_at"].replace(" ", "T"))
    
    for key, value in activity_data.items():
        setattr(activity, key, value)
    
    db.commit()
    db.refresh(activity)
    
    return {"message": "Activity updated"}


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(activity_id: int, db: Session = Depends(get_db)):
    """
    Delete a pedagogical activity.
    
    Args:
        activity_id (int): The unique identifier of the activity to delete.
        db (Session): Database session provided by dependency injection.
    
    Raises:
        HTTPException: 404 error if activity is not found.
    """
    # Find and delete activity from the database
    activity = db.query(ActivitePedagogiqueModel).filter(
        ActivitePedagogiqueModel.id_activite == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    db.delete(activity)
    db.commit()


@router.get("/{activity_id}/exercises")
def get_activity_exercises(activity_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all exercises included in a specific activity.
    
    Args:
        activity_id (int): The unique identifier of the activity.
        db (Session): Database session provided by dependency injection.
    
    Returns:
        list: List of exercise dictionaries associated with the activity.
    
    Raises:
        HTTPException: 404 error if activity is not found.
    """
    # get activity and extract exercise IDs
    activity = db.query(ActivitePedagogiqueModel).filter(
        ActivitePedagogiqueModel.id_activite == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    exercise_ids = from_json(activity.ids_exercices_inclus)
    exercises = db.query(ExerciceInstanceModel).filter(
        ExerciceInstanceModel.id_exercice.in_(exercise_ids)
    ).all() if exercise_ids else []
    
    return {
        "exercises": [
            {
                "id_exercice": e.id_exercice,
                "nom": e.nom,
                "description": e.description,
            }
            for e in exercises
        ]
    }


@router.post("/{activity_id}/exercises/{exercise_id}", status_code=status.HTTP_201_CREATED)
def add_exercise_to_activity(activity_id: int, exercise_id: int, db: Session = Depends(get_db)):
    """
    Add an exercise to an activity.
    
    Args:
        activity_id (int): The unique identifier of the activity.
        exercise_id (int): The unique identifier of the exercise.
        db (Session): Database session provided by dependency injection.
    
    Returns:
        dict: Dictionary with success message.
    
    Raises:
        HTTPException: 404 error if activity is not found.
    """
    activity = db.query(ActivitePedagogiqueModel).filter(
        ActivitePedagogiqueModel.id_activite == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Get current exercises list
    exercise_ids = from_json(activity.ids_exercices_inclus) or []
    
    # Add exercise if not already present
    if exercise_id not in exercise_ids:
        exercise_ids.append(exercise_id)
        activity.ids_exercices_inclus = to_json(exercise_ids)
        db.commit()
    
    return {"message": "Exercise added successfully"}


@router.delete("/{activity_id}/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_exercise_from_activity(activity_id: int, exercise_id: int, db: Session = Depends(get_db)):
    """
    Remove an exercise from an activity.
    
    Args:
        activity_id (int): The unique identifier of the activity.
        exercise_id (int): The unique identifier of the exercise.
        db (Session): Database session provided by dependency injection.
    
    Raises:
        HTTPException: 404 error if activity is not found.
    """
    activity = db.query(ActivitePedagogiqueModel).filter(
        ActivitePedagogiqueModel.id_activite == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Get current exercises list
    exercise_ids = from_json(activity.ids_exercices_inclus) or []
    
    # Remove exercise if present
    if exercise_id in exercise_ids:
        exercise_ids.remove(exercise_id)
        activity.ids_exercices_inclus = to_json(exercise_ids)
        db.commit()


@router.put("/{activity_id}/exercises/reorder", status_code=status.HTTP_200_OK)
def reorder_exercises(activity_id: int, ordered_exercise_ids: list = Body(...), db: Session = Depends(get_db)):
    """
    Reorder exercises within an activity.
    
    Args:
        activity_id (int): The unique identifier of the activity.
        ordered_exercise_ids (list): List of exercise IDs in the new order.
        db (Session): Database session provided by dependency injection.
    
    Returns:
        dict: Dictionary with success message.
    
    Raises:
        HTTPException: 404 error if activity is not found.
    """
    activity = db.query(ActivitePedagogiqueModel).filter(
        ActivitePedagogiqueModel.id_activite == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Update the exercise order
    activity.ids_exercices_inclus = to_json(ordered_exercise_ids)
    db.commit()
    
    return {"message": "Exercises reordered successfully"}


@router.post("/{activity_id}/start")
def start_activity(activity_id: int, learner_data: dict, db: Session = Depends(get_db)):
    """
    Start an activity session for a learner.
    
    Args:
        activity_id (int): The unique identifier of the activity.
        learner_data (dict): Dictionary containing learner information (id_apprenant).
        db (Session): Database session provided by dependency injection.
    
    Returns:
        dict: Dictionary with session ID and activity name.
    
    Raises:
        HTTPException: 404 error if activity is not found.
    """
    # validate activity exists
    activity = db.query(ActivitePedagogiqueModel).filter(
        ActivitePedagogiqueModel.id_activite == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    learner_id = learner_data.get("id_apprenant")
    
    # Créer une nouvelle session d'apprentissage pour l'apprenant
    session = SessionApprenantModel(
        id_apprenant=learner_id,
        id_activite=activity_id,
        date_debut=datetime.utcnow(),
        statut="started"
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {
        "id_session": session.id_session,
        "message": f"Activity started for learner {learner_id}",
        "activity": activity.nom,
    }


@router.post("/{activity_id}/submit-attempt")
def submit_attempt(activity_id: int, attempt_data: dict, db: Session = Depends(get_db)):
    """
    Submit an attempt for an exercise in an activity.
    
    Args:
        activity_id (int): The unique identifier of the activity.
        attempt_data (dict): Dictionary containing attempt information 
                            (id_exercice_ou_evenement, id_apprenant, id_aav_cible, 
                             score_obtenu, est_valide, temps_resolution_secondes).
        db (Session): Database session provided by dependency injection.
    
    Returns:
        dict: Dictionary with tentative ID and success message.
    
    Raises:
        HTTPException: 404 error if activity is not found.
    """
    # validate activity exists
    activity = db.query(ActivitePedagogiqueModel).filter(
        ActivitePedagogiqueModel.id_activite == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # save attempt/tentative to database
    tentative = TentativeModel(
        id_exercice_ou_evenement=attempt_data.get("id_exercice_ou_evenement"),
        id_apprenant=attempt_data.get("id_apprenant"),
        id_aav_cible=attempt_data.get("id_aav_cible"),
        score_obtenu=attempt_data.get("score_obtenu", 0.0),
        est_valide=attempt_data.get("est_valide", False),
        temps_resolution_secondes=attempt_data.get("temps_resolution_secondes"),
    )
    
    db.add(tentative)
    db.commit()
    db.refresh(tentative)
    
    return {
        "id_tentative": tentative.id,
        "message": "Attempt submitted",
    }


@router.post("/{activity_id}/complete")
def complete_activity(activity_id: int, session_data: dict, db: Session = Depends(get_db)):
    """
    Mark an activity session as complete and calculate learning summary.
    
    Args:
        activity_id (int): The unique identifier of the activity.
        session_data (dict): Dictionary containing session information (id_session).
        db (Session): Database session provided by dependency injection.
    
    Returns:
        dict: Dictionary with session ID, success message, and learning summary (bilan).
    
    Raises:
        HTTPException: 404 error if session is not found.
    """
    # Récupérer la session
    session = db.query(SessionApprenantModel).filter(
        SessionApprenantModel.id_session == session_data.get("id_session")
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.date_fin = datetime.utcnow()
    session.statut = "closed"
    # calculate learning summary from all learner attempts
    tentatives = db.query(TentativeModel).filter(
        TentativeModel.id_apprenant == session.id_apprenant
    ).all()
    
    bilan = {
        "total_attempts": len(tentatives),
        "valid_attempts": sum(1 for t in tentatives if t.est_valide),
        "average_score": sum(t.score_obtenu or 0 for t in tentatives) / len(tentatives) if tentatives else 0,
    }
    
    session.bilan_session = to_json(bilan)
    
    db.commit()
    db.refresh(session)
    
    return {
        "id_session": session.id_session,
        "message": "Activity completed",
        "bilan": bilan,
    }
