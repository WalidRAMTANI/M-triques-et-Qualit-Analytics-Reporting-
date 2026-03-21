# app/routers/activitePedagogique_sqlalchemy.py
"""
Router for Pedagogical Activities (Group 4) using SQLAlchemy ORM.

This module provides RESTful API endpoints for managing pedagogical activities,
including activity CRUD operations, exercise management, and learner session tracking.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.database_models import (
    ActivitePedagogique, 
    ExerciceDetail, 
    Tentative, 
    SessionApprenant,
    AAV,
    Apprenant
)
import json
from datetime import datetime

router = APIRouter(prefix="/activities", tags=["Activities"])


def get_db():
    """
    Dependency function to provide database session.
    
    Yields a SQLAlchemy Session object and ensures proper cleanup.
    
    Returns:
        Session: SQLAlchemy session for database operations
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def from_json(data):
    """
    Convert JSON string to Python object.
    
    Args:
        data: String, dict, or list to convert.
    
    Returns:
        dict or list: Parsed JSON object, or empty list if parsing fails.
    """
    if isinstance(data, str):
        try:
            # parse JSON string into Python object
            return json.loads(data)
        except:
            return []
    return data or []


def to_json(data):
    """
    Convert Python object to JSON string.
    
    Args:
        data: Dictionary or list to convert.
    
    Returns:
        str: JSON string representation of the object.
    """
    if isinstance(data, (list, dict)):
        # convert to JSON string
        return json.dumps(data)
    return data


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
    activities = db.query(ActivitePedagogique).all()
    
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
    # retrieve activity by ID
    activity = db.query(ActivitePedagogique).filter(
        ActivitePedagogique.id_activite == activity_id
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


@router.post("/")
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
    
    db_activity = ActivitePedagogique(**activity_data)
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
    # find activity and update its fields
    activity = db.query(ActivitePedagogique).filter(
        ActivitePedagogique.id_activite == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    if "ids_exercices_inclus" in activity_data:
        activity_data["ids_exercices_inclus"] = to_json(activity_data["ids_exercices_inclus"])
    
    for key, value in activity_data.items():
        setattr(activity, key, value)
    
    db.commit()
    db.refresh(activity)
    
    return {"message": "Activity updated"}


@router.delete("/{activity_id}")
def delete_activity(activity_id: int, db: Session = Depends(get_db)):
    """
    Delete a pedagogical activity.
    
    Args:
        activity_id (int): The unique identifier of the activity to delete.
        db (Session): Database session provided by dependency injection.
    
    Returns:
        dict: Dictionary with success message.
    
    Raises:
        HTTPException: 404 error if activity is not found.
    """
    # find and delete activity from database
    activity = db.query(ActivitePedagogique).filter(
        ActivitePedagogique.id_activite == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    db.delete(activity)
    db.commit()
    
    return {"message": "Activity deleted"}


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
    activity = db.query(ActivitePedagogique).filter(
        ActivitePedagogique.id_activite == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    exercise_ids = from_json(activity.ids_exercices_inclus)
    exercises = db.query(ExerciceDetail).filter(
        ExerciceDetail.id_exercice.in_(exercise_ids)
    ).all() if exercise_ids else []
    
    return [
        {
            "id_exercice": e.id_exercice,
            "nom": e.nom,
            "description": e.description,
        }
        for e in exercises
    ]


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
    activity = db.query(ActivitePedagogique).filter(
        ActivitePedagogique.id_activite == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    learner_id = learner_data.get("id_apprenant")
    
    # create new learning session for learner
    session = SessionApprenant(
        id_apprenant=learner_id,
        id_activite=activity_id,
        debut_session=datetime.utcnow(),
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
    activity = db.query(ActivitePedagogique).filter(
        ActivitePedagogique.id_activite == activity_id
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # save attempt/tentative to database
    tentative = Tentative(
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
    # retrieve the session
    session = db.query(SessionApprenant).filter(
        SessionApprenant.id_session == session_data.get("id_session")
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.fin_session = datetime.utcnow()
    
    # calculate learning summary from all learner attempts
    tentatives = db.query(Tentative).filter(
        Tentative.id_apprenant == session.id_apprenant
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
