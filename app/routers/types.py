from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import AAVModel, get_db

router = APIRouter(tags=["Types"])


@router.get("/activity-types")
def get_activity_types():
    return {
        "types": [
            "pilotee",
            "prof_definie",
            "revision"
        ]
    }


@router.get("/mastery-levels")
def get_mastery_levels()->dict:
    return {
        "levels": {
            "master": 0.9,
            "intermediate": 0.5,
            "novice": 0.0
        }
    }


@router.get("/disciplines")
def get_disciplines(db: Session = Depends(get_db)):
    """
    Retrieve unique disciplines from the AAV table.
    """
    # Query distinct disciplines from AAVModel
    disciplines = db.query(AAVModel.discipline).distinct().all()
    # Flatten the result list of tuples
    discipline_list = [d[0] for d in disciplines if d[0]]
    
    # If no disciplines in DB, fallback to defaults
    if not discipline_list:
        discipline_list = ["Mathématiques", "Français", "Informatique"]
        
    return {
        "disciplines": sorted(discipline_list)
    }
