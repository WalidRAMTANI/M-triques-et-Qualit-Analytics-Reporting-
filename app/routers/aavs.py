# app/routers/aavs_sqlalchemy.py
"""
Router for AAVs (Learning Outcomes) using SQLAlchemy ORM.

This module provides RESTful API endpoints for managing AAVs (Acquis d'Apprentissage Visés),
which represent the learning outcomes or competencies that students should achieve.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal, AAVModel, get_db

router = APIRouter(prefix="/aavs", tags=["AAVs"])

@router.get("/")
def get_aavs(discipline: str = None, db: Session = Depends(get_db)):
    """
    Retrieve all AAVs with optional filtering by discipline.
    
    Args:
        discipline (str, optional): Filter results by discipline name. Defaults to None.
        db (Session): Database session provided by dependency injection.
    
    Returns:
        list: List of AAV dictionaries containing id_aav, nom, libelle_integration,
              discipline and enseignement.
    """
    # Filter by discipline if provided
    query = db.query(AAVModel)
    if discipline:
        query = query.filter(AAVModel.discipline == discipline)
    
    aavs = query.all()
    return [
        {
            "id_aav": aav.id_aav,
            "nom": aav.nom,
            "libelle_integration": aav.libelle_integration,
            "discipline": aav.discipline,
            "enseignement": aav.enseignement,
            "type_aav": getattr(aav, "type_aav", "N/A"),
            "type_evaluation": getattr(aav, "type_evaluation", "N/A"),
            "is_active": getattr(aav, "is_active", True),
        }
        for aav in aavs
    ]


@router.get("/{aav_id}")
def get_aav(aav_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific AAV by its ID.
    
    Args:
        aav_id (int): The unique identifier of the AAV to retrieve.
        db (Session): Database session provided by dependency injection.
    
    Returns:
        dict: AAV dictionary containing all fields including id_aav, nom,
              libelle_integration, discipline, enseignement, description_markdown,
              type_aav, type_evaluation, prerequis_ids, is_active, version,
              created_at, and updated_at.
    
    Raises:
        HTTPException: 404 error if AAV with given ID is not found.
    """
    # Retrieve AAV by ID from database
    aav = db.query(AAVModel).filter(AAVModel.id_aav == aav_id).first()
    if not aav:
        raise HTTPException(status_code=404, detail="AAV not found")
    
    return {
        "id_aav": aav.id_aav,
        "nom": aav.nom,
        "libelle_integration": aav.libelle_integration,
        "discipline": aav.discipline,
        "enseignement": aav.enseignement,
        "description_markdown": aav.description_markdown,
        "id_enseignant": aav.id_enseignant,
        "type_aav": getattr(aav, "type_aav", "N/A"),
        "type_evaluation": getattr(aav, "type_evaluation", "N/A"),
        "prerequis_ids": getattr(aav, "prerequis_ids", []),
        "prerequis_externes_codes": getattr(aav, "prerequis_externes_codes", []),
        "code_prerequis_interdisciplinaire": getattr(aav, "code_prerequis_interdisciplinaire", ""),
        "aav_enfant_ponderation": getattr(aav, "aav_enfant_ponderation", {}),
        "ids_exercices": getattr(aav, "ids_exercices", []),
        "prompts_fabrication_ids": getattr(aav, "prompts_fabrication_ids", []),
        "regles_progression": getattr(aav, "regles_progression", {}),
        "is_active": getattr(aav, "is_active", True),
        "version": getattr(aav, "version", 1),
        "created_at": getattr(aav, "created_at", None),
        "updated_at": getattr(aav, "updated_at", None),
    }


@router.post("/")
def create_aav(aav_data: dict, db: Session = Depends(get_db)):
    """
    Create a new AAV record.
    
    Args:
        aav_data (dict): Dictionary containing AAV fields (nom, discipline, etc.).
        db (Session): Database session provided by dependency injection.
    
    Returns:
        dict: Dictionary with id_aav, nom of the created AAV, and a success message.
    """
    # Create new AAV instance and save to database
    db_aav = AAVModel(**aav_data)
    db.add(db_aav)
    db.commit()
    db.refresh(db_aav)
    
    return {
        "id_aav": db_aav.id_aav,
        "nom": db_aav.nom,
        "message": "AAV created"
    }


@router.put("/{aav_id}")
def update_aav(aav_id: int, aav_data: dict, db: Session = Depends(get_db)):
    """
    Update an existing AAV record.
    
    Args:
        aav_id (int): The unique identifier of the AAV to update.
        aav_data (dict): Dictionary containing fields to update.
        db (Session): Database session provided by dependency injection.
    
    Returns:
        dict: Dictionary with id_aav, nom of the updated AAV, and a success message.
    
    Raises:
        HTTPException: 404 error if AAV with given ID is not found.
    """
    # Find AAV and update its fields
    aav = db.query(AAVModel).filter(AAVModel.id_aav == aav_id).first()
    if not aav:
        raise HTTPException(status_code=404, detail="AAV not found")
    
    for key, value in aav_data.items():
        setattr(aav, key, value)
    
    db.commit()
    db.refresh(aav)
    
    return {
        "id_aav": aav.id_aav,
        "nom": aav.nom,
        "message": "AAV updated"
    }


@router.delete("/{aav_id}")
def delete_aav(aav_id: int, db: Session = Depends(get_db)):
    """
    Delete an AAV record.
    
    Args:
        aav_id (int): The unique identifier of the AAV to delete.
        db (Session): Database session provided by dependency injection.
    
    Returns:
        dict: Dictionary with a success message.
    
    Raises:
        HTTPException: 404 error if AAV with given ID is not found.
    """
    # Find and delete the AAV from database
    aav = db.query(AAVModel).filter(AAVModel.id_aav == aav_id).first()
    if not aav:
        raise HTTPException(status_code=404, detail="AAV not found")
    
    db.delete(aav)
    db.commit()
    
    return {"message": "AAV deleted"}
