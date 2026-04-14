import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app
from app.database import ApprenantModel, StatutApprentissageModel, AAVModel
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
    with patch("app.routers.learners.get_db_connection") as mock:
        @contextmanager
        def mock_conn():
            yield db_session
        mock.side_effect = mock_conn
        yield mock

def test_list_learners_real(db_session, mock_db_connection):
    l = ApprenantModel(id_apprenant=1, nom_utilisateur="test_user", email="test@example.com", is_active=True)
    db_session.add(l)
    db_session.commit()
    
    response = client.get("/learners/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["nom_utilisateur"] == "test_user"

def test_get_learner_real(db_session, mock_db_connection):
    l = ApprenantModel(id_apprenant=2, nom_utilisateur="user2", email="user2@test.com", is_active=True)
    db_session.add(l)
    db_session.commit()
    
    response = client.get("/learners/2")
    assert response.status_code == 200
    assert response.json()["nom_utilisateur"] == "user2"

def test_create_learner_real(db_session, mock_db_connection):
    payload = {"id_apprenant": 3, "nom_utilisateur": "user3", "email": "user3@test.com"}
    response = client.post("/learners/", json=payload)
    assert response.status_code == 201
    assert response.json()["id_apprenant"] == 3


