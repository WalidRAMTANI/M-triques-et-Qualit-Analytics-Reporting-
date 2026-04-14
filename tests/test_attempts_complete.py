import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app
from app.database import TentativeModel, StatutApprentissageModel
from datetime import datetime

client = TestClient(app)

from app.database import SessionLocal, init_database, get_db_connection
from contextlib import contextmanager

@pytest.fixture
def db_session():
    from app.database import engine, Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def mock_db_connection(db_session):
    with patch("app.routers.attempts.get_db_connection") as mock:
        @contextmanager
        def mock_conn():
            yield db_session
        mock.side_effect = mock_conn
        yield mock

def test_list_attempts_real(db_session, mock_db_connection):
    mock_att = TentativeModel(
        id=1, id_exercice_ou_evenement=101, id_apprenant=1, id_aav_cible=1,
        score_obtenu=0.8, date_tentative=datetime.now(), est_valide=True
    )
    db_session.add(mock_att)
    db_session.commit()
    
    response = client.get("/attempts")
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_create_attempt_real(db_session, mock_db_connection):
    # Need to add learner, aav if constraints are active
    # But for now let's just try
    payload = {
        "id_exercice_ou_evenement": 102,
        "id_apprenant": 1,
        "id_aav_cible": 1,
        "score_obtenu": 0.9,
        "est_valide": True
    }
    
    # We should add the learner and aav to avoid Foreign Key errors
    from app.database import ApprenantModel, AAVModel
    db_session.add(ApprenantModel(id_apprenant=1, nom_utilisateur="user1", email="user1@test.com"))
    db_session.add(AAVModel(id_aav=1, nom="AAV1", discipline="Informatique"))
    db_session.commit()

    response = client.post("/attempts", json=payload)
    assert response.status_code == 201
    assert response.json()["score_obtenu"] == 0.9

def test_process_attempt_real(db_session, mock_db_connection):
    from app.database import ApprenantModel, AAVModel, StatutApprentissageModel
    db_session.add(ApprenantModel(id_apprenant=1, nom_utilisateur="user1", email="u1@test.com"))
    db_session.add(AAVModel(id_aav=1, nom="AAV1", discipline="Informatique"))
    
    att = TentativeModel(
        id=1, id_exercice_ou_evenement=101, id_apprenant=1, id_aav_cible=1, 
        score_obtenu=1.0, date_tentative=datetime.now()
    )
    db_session.add(att)
    db_session.commit()
    
    response = client.post("/attempts/1/process")
    assert response.status_code == 200
    assert "nouveau_niveau" in response.json()

