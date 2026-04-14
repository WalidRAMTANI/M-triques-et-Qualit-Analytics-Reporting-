import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from contextlib import contextmanager
from app.main import app
from app.database import (
    AAVModel, ApprenantModel, PromptFabricationAAVModel, ExerciceInstanceModel,
    TentativeExerciceModel, SessionLocal, init_database
)
from datetime import datetime

client = TestClient(app)
from app.database import DATABASE_URL
print(f"DEBUG: DATABASE_URL={DATABASE_URL}")
def mock_aav(id_aav=1):
    return AAVModel(
        id_aav=id_aav,
        nom="AAV Test",
        type_evaluation="Calcul Automatisé",
        discipline="Maths",
        is_active=True,
        regles_progression='{"seuil_succes": 0.7}'
    )

def mock_prompt(id_prompt=1, id_aav=1):
    return PromptFabricationAAVModel(
        id_prompt=id_prompt,
        cible_aav_id=id_aav,
        prompt_texte="Test Prompt",
        is_active=True,
        version_prompt=1
    )

def mock_exercice(id_exercice=1, id_aav=1, id_prompt=1):
    return ExerciceInstanceModel(
        id_exercice=id_exercice,
        id_prompt_source=id_prompt,
        id_aav_cible=id_aav,
        titre="Exercice Test",
        difficulte="debutant",
        taux_succes_moyen=0.8,
        contenu='{"solution": "42"}'
    )

@pytest.fixture
def db_session():
    from app.database import engine, Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

def test_get_prompts_for_aav_real(db_session):
    from app.database import DATABASE_URL
    print(f"DEBUG: DATABASE_URL={DATABASE_URL}")
    aav = mock_aav(id_aav=1)
    prompt = mock_prompt(id_prompt=1, id_aav=1)
    db_session.add(aav)
    db_session.add(prompt)
    db_session.commit()
    
    response = client.get("/aavs/1/prompts")
    if response.status_code != 200:
        print(f"FAILED: {response.json()}")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_best_prompt_for_aav_real(db_session):
    aav = mock_aav(id_aav=2)
    p1 = mock_prompt(id_prompt=2, id_aav=2)
    p2 = mock_prompt(id_prompt=3, id_aav=2)
    e1 = mock_exercice(id_exercice=1, id_aav=2, id_prompt=2)
    e1.taux_succes_moyen = 0.9
    e2 = mock_exercice(id_exercice=2, id_aav=2, id_prompt=3)
    e2.taux_succes_moyen = 0.5
    
    db_session.add_all([aav, p1, p2, e1, e2])
    db_session.commit()
    
    response = client.get("/aavs/2/prompts/best")
    if response.status_code != 200:
        print(f"FAILED: {response.json()}")
    assert response.status_code == 200
    assert response.json()["id_prompt"] == 2

def test_evaluate_exercise_real(db_session):
    aav = mock_aav(id_aav=3)
    p = mock_prompt(id_prompt=4, id_aav=3)
    e = mock_exercice(id_exercice=3, id_aav=3, id_prompt=4)
    e.contenu = '{"solution": "42"}'
    db_session.add_all([aav, p, e])
    db_session.commit()
    
    payload = {
        "id_exercice": 3,
        "reponse_apprenant": "42",
        "type_evaluation": "Calcul Automatisé"
    }
    
    response = client.post("/exercises/evaluate", json=payload)
    if response.status_code != 200:
        print(f"FAILED: {response.json()}")
    assert response.status_code == 200
    assert response.json()["score_obtenu"] == 1.0


