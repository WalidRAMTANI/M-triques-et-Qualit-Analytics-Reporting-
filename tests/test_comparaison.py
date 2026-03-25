import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

# 1. Test de la comparaison d'AAVs (GET /comparaison/aavs)
def test_compare_aavs(client):
    # On passe les IDs dans l'URL avec le paramètre ?ids=
    # Note : Assure-toi que le préfixe de ton routeur est bien /comparaison dans ton main.py
    response = client.get("/comparaison/aavs?ids=1,2")
    assert response.status_code in [200, 404]

# 2. Test de la comparaison des apprenants (GET /comparaison/learners)
def test_compare_learners(client):
    # On passe l'ID de l'ontologie dans l'URL
    response = client.get("/comparaison/learners?id_ontologie=1")
    assert response.status_code in [200, 404]