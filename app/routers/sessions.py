# app/routers/sessions.py
"""
Router for managing learning sessions using SQLAlchemy ORM.

This module provides RESTful API endpoints for managing learner sessions,
including session creation, retrieval, and deletion.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import (
    get_db, SessionApprenantModel, ActivitePedagogiqueModel, 
    TentativeModel, ApprenantModel, from_json, to_json
)

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.get("/")
def list_sessions(db: Session = Depends(get_db)):
    """
    Retrieve all learning sessions.
    
    Args:
        db (Session): Database session provided by dependency injection.
    
    Returns:
        dict: Dictionary containing list of sessions.
    """
    sessions = db.query(SessionApprenantModel).all()
    
    return {
        "sessions": [
            {
                "id_session": s.id_session,
                "id_activite": s.id_activite,
                "id_apprenant": s.id_apprenant,
                "date_debut": s.date_debut.isoformat() if s.date_debut else None,
                "statut": s.statut,
            }
            for s in sessions
        ]
    }


@router.get("/{session_id}")
def get_session(session_id: int, db: Session = Depends(get_db)):
    """
    Retrieve details of a specific learning session.
    
    Args:
        session_id (int): The unique identifier of the session.
        db (Session): Database session provided by dependency injection.
    
    Returns:
        dict: Dictionary with session details.
    
    Raises:
        HTTPException: 404 error if session is not found.
    """
    session = db.query(SessionApprenantModel).filter(
        SessionApprenantModel.id_session == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "id_session": session.id_session,
        "id_activite": session.id_activite,
        "id_apprenant": session.id_apprenant,
        "date_debut": session.date_debut.isoformat() if session.date_debut else None,
        "date_fin": session.date_fin.isoformat() if session.date_fin else None,
        "statut": session.statut,
        "bilan": from_json(session.bilan_session) if session.bilan_session else None,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_session(session_data: dict, db: Session = Depends(get_db)):
    """
    Create a new learning session.
    
    Args:
        session_data (dict): Dictionary containing session information (id_activite, id_apprenant).
        db (Session): Database session provided by dependency injection.
    
    Returns:
        dict: Dictionary with session ID.
    
    Raises:
        HTTPException: 404 error if activity or learner is not found.
    """
    # Verify activity exists
    activity = db.query(ActivitePedagogiqueModel).filter(
        ActivitePedagogiqueModel.id_activite == session_data.get("id_activite")
    ).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Verify learner exists
    learner = db.query(ApprenantModel).filter(
        ApprenantModel.id_apprenant == session_data.get("id_apprenant")
    ).first()
    
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found")
    
    # Create new session
    new_session = SessionApprenantModel(
        id_activite=session_data["id_activite"],
        id_apprenant=session_data["id_apprenant"],
        date_debut=datetime.utcnow(),
        statut="created"
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return {"id_session": new_session.id_session}


@router.put("/{session_id}/start", status_code=status.HTTP_200_OK)
def start_session(session_id: int, db: Session = Depends(get_db)):
    """
    Start a learning session.
    
    Args:
        session_id (int): The unique identifier of the session.
        db (Session): Database session provided by dependency injection.
    
    Returns:
        dict: Dictionary with success message.
    
    Raises:
        HTTPException: 404 error if session is not found.
    """
    session = db.query(SessionApprenantModel).filter(
        SessionApprenantModel.id_session == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.statut = "started"
    db.commit()
    
    return {"message": "Session started"}


@router.put("/{session_id}/close", status_code=status.HTTP_200_OK)
def close_session(session_id: int, db: Session = Depends(get_db)):
    """
    Close/end a learning session.
    
    Args:
        session_id (int): The unique identifier of the session.
        db (Session): Database session provided by dependency injection.
    
    Returns:
        dict: Dictionary with success message and session summary.
    
    Raises:
        HTTPException: 404 error if session is not found.
    """
    session = db.query(SessionApprenantModel).filter(
        SessionApprenantModel.id_session == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.date_fin = datetime.utcnow()
    session.statut = "closed"
    
    # Calculate learning summary from all learner attempts
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
    
    return {
        "message": "Session closed",
        "summary": bilan
    }


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: int, db: Session = Depends(get_db)):
    """
    Delete a learning session.
    
    Args:
        session_id (int): The unique identifier of the session to delete.
        db (Session): Database session provided by dependency injection.
    
    Raises:
        HTTPException: 404 error if session is not found.
    """
    session = db.query(SessionApprenantModel).filter(
        SessionApprenantModel.id_session == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(session)
    db.commit()
