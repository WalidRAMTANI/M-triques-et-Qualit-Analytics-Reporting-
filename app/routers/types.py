# app/routers/types.py
"""
Router for retrieving system types and enumerations.

This module provides RESTful API endpoints for accessing available types,
such as activity types, mastery levels, and disciplines.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/types", tags=["Types"])


@router.get("/activity-types")
def get_activity_types():
    """
    Retrieve available activity types.
    
    Returns:
        dict: Dictionary containing list of supported activity types 
              (pilotee, prof_definie, revision).
    """
    return {
        "types": [
            "pilotee",
            "prof_definie",
            "revision"
        ]
    }


@router.get("/mastery-levels")
def get_mastery_levels()->dict:
    """
    Retrieve mastery level thresholds for learning assessment.
    
    Returns:
        dict: Dictionary with mastery level names and their numeric thresholds:
              - master: 0.9 (90% mastery)
              - intermediate: 0.5 (50% mastery)
              - novice: 0.0 (0% mastery)
    """
    return {
        "levels": {
            "master": 0.9,
            "intermediate": 0.5,
            "novice": 0.0
        }
    }


@router.get("/disciplines")
def get_disciplines():
    """
    Retrieve available disciplines/subjects.
    
    Returns:
        dict: Dictionary containing list of available teaching disciplines.
    """
    return {
        "disciplines": [
            "Mathématiques",
            "Français",
            "Histoire-Géographie",
            "Sciences",
            "Informatique"
        ]
    }
