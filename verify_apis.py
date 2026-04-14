from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_routes():
    # Test root / docs
    response = client.get("/docs")
    print(f"GET /docs: {response.status_code}")

    # Test AAVs
    response = client.get("/aavs/")
    print(f"GET /aavs/: {response.status_code}")
    if response.status_code == 200:
        aavs = response.json()
        print(f"  Found {len(aavs)} AAVs")
    else:
        print(f"  Error: {response.text}")

    # Test Learners
    response = client.get("/learners/")
    print(f"GET /learners/: {response.status_code}")
    if response.status_code == 200:
        learners = response.json()
        print(f"  Found {len(learners)} Learners")
    else:
        print(f"  Error: {response.text}")

    # Test Dashboard (Teacher 1)
    response = client.get("/dashboard/teachers/1/overview")
    print(f"GET /dashboard/teachers/1/overview: {response.status_code}")
    if response.status_code != 200:
        print(f"  Error: {response.text}")

    # Test Ontologies
    response = client.get("/ontologies/")
    print(f"GET /ontologies/: {response.status_code}")
    if response.status_code == 200:
        ontologies = response.json()
        print(f"  Found {len(ontologies)} Ontologies")

    # Test Metrics
    response = client.get("/metrics/aav/")
    print(f"GET /metrics/aav/: {response.status_code}")

    # Test Alerts
    response = client.get("/alerts/fragile-aavs")
    print(f"GET /alerts/fragile-aavs: {response.status_code}")

if __name__ == "__main__":
    test_routes()
