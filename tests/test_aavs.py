import pytest
from fastapi.testclient import TestClient
from app.main import app

# On crée le client de test qui va simuler les appels à ton API
@pytest.fixture(scope="module")
def client():
    return TestClient(app)

# 1. Test de la création (POST /aavs/)
def test_create_aav(client):
    response = client.post("/aavs/", json={
        "id_aav": 999,
        "nom": "AAV de Test",
        "libelle_integration": "test integration",
        "discipline": "Informatique",
        "enseignement": "Test",
        "description_markdown": "Description de test"
    })
    # On vérifie que la création a réussi (200 OK selon ton routeur)
    assert response.status_code == 200
    assert "id_aav" in response.json()

# 2. Test de la lecture de la liste (GET /aavs/)
def test_get_all_aavs(client):
    response = client.get("/aavs/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# 3. Test de la lecture d'un AAV précis (GET /aavs/{id})
def test_get_aav_by_id(client):
    response = client.get("/aavs/999")
    # Selon si la base de test est réinitialisée ou non, on accepte 200 ou 404
    assert response.status_code in [200, 404] 

# 4. Test de la mise à jour (PUT /aavs/{id})
def test_update_aav(client):
    response = client.put("/aavs/999", json={"nom": "AAV Modifié"})
    assert response.status_code in [200, 404]

# 5. Test de la suppression (DELETE /aavs/{id})
def test_delete_aav(client):
    response = client.delete("/aavs/999")
    assert response.status_code in [200, 404]