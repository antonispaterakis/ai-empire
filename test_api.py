from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_generate_endpoint():
    response = client.post("/generate", json={"topic": "AI Automation", "auto_post": False})
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["message"] == "Generation task started"

def test_status_endpoint():
    # First trigger a task
    response = client.post("/generate", json={"topic": "Microservices", "auto_post": False})
    task_id = response.json()["task_id"]

    # Then check status
    status_response = client.get(f"/status/{task_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["task_id"] == task_id
    assert "status" in status_data
    assert "result" in status_data
