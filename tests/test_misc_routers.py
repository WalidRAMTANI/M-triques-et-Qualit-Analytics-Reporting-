import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from contextlib import contextmanager
from app.main import app
from app.database import (
    ApprenantModel, AAVModel, StatutApprentissageModel, 
    SessionLocal, init_database
)
from datetime import datetime

client = TestClient(app)

@pytest.fixture
def db_session():
    from app.database import engine, Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def mock_db(db_session):
    # Dependency override for 'get_db' (used in aavs.py)
    from app.database import get_db
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    
    # Patch 'get_db_connection' (used in statuts.py)
    with patch("app.routers.statuts.get_db_connection") as mock_conn_statuts:
        @contextmanager
        def mock_c():
            yield db_session
        mock_conn_statuts.side_effect = mock_c
        yield db_session
    
    app.dependency_overrides.clear()

def test_list_aavs_real(db_session, mock_db):
    a = AAVModel(
        id_aav=1, nom="AAV1", discipline="Maths", 
        libelle_integration="maths", enseignement="Algèbre",
        description_markdown="Description test",
        type_aav="Atomique", type_evaluation="Calcul Automatisé",
        is_active=True
    )
    db_session.add(a)
    db_session.commit()
    
    response = client.get("/aavs/")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_update_learning_status_real(db_session, mock_db):
    db_session.add(ApprenantModel(id_apprenant=1, nom_utilisateur="u1", email="u1@test.com"))
    db_session.add(AAVModel(id_aav=1, nom="AAV1", discipline="Maths"))
    
    stat = StatutApprentissageModel(
        id=1, id_apprenant=1, id_aav_cible=1, 
        niveau_maitrise=0.5, est_maitrise=False,
        date_debut_apprentissage=datetime.now()
    )
    db_session.add(stat)
    db_session.commit()

    payload = {"niveau_maitrise": 0.8, "historique_tentatives_ids": [1]}
    response = client.put("/learning-status/1", json=payload)
    assert response.status_code == 200
    assert response.json()["niveau_maitrise"] == 0.8

def test_difficult_aavs():
    with patch("app.routers.alerts.detecter_aavs_difficiles") as mock_detect:
        mock_detect.return_value = [
            {
                "id_aav": 1, "nom": "AAV1", "taux_succes": 0.2, 
                "nb_tentatives": 10, "suggestion": "Refaire cours"
            }
        ]
        response = client.get("/alerts/difficult-aavs")
        assert response.status_code == 200
        assert response.json()[0]["id_aav"] == 1

def test_global_report():
    with patch("app.routers.reports.generer_rapport_global") as mock_gen:
        mock_gen.return_value = {
            "titre": "Rapport Global",
            "date_generation": datetime.now().isoformat(),
            "nb_aavs_total": 10,
            "nb_aavs_utilisables": 8,
            "nb_alertes": {},
            "alertes": {},
            "aavs": [],
            "contenu": {"stats": "data"},
            "format": "json"
        }
        response = client.get("/reports/global")
        assert response.status_code == 200
        assert response.json()["titre"] == "Rapport Global"
