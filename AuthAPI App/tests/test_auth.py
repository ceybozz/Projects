from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "AuthAPI is running."}

def test_register_login():
    email = "test@example.com"
    password = "secret123"
    response = client.post("/register", json={"email": email, "password": password})
    assert response.status_code == 200
    assert "access_token" in response.json()
    response = client.post("/login", json={"email": email, "password": password})
    assert response.status_code == 200
    assert "access_token" in response.json()
