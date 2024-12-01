import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def test_client():
    """Fixture para usar el cliente de pruebas"""
    return client

# Test para el endpoint de la página principal
def test_home_endpoint(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert "Salus AI" in response.text  # Asegura que el texto clave aparece

# Test para el endpoint de /routine
def test_routine_endpoint(test_client):
    response = test_client.post(
        "/routine",
        data={
            "level": "Principiante",
            "time": 30,
            "equipment": "Mancuernas",
            "goal": "Ganar músculo"
        }
    )
    assert response.status_code == 200
    assert "html" in response.text.lower()  # Asegura que devuelve una página HTML

# Test para el endpoint de /dieta
def test_dieta_endpoint(test_client):
    response = test_client.post(
        "/dieta",
        data={
            "goal": "Perder peso",
            "preferences": "Sin gluten"
        }
    )
    assert response.status_code == 200
    assert "html" in response.text.lower()  # Asegura que devuelve una página HTML

# Test para el endpoint de /supplements
def test_supplements_endpoint(test_client):
    response = test_client.post(
        "/suplementos",
        data={
            "goal": "Ganar músculo",
            "diet_type": "Keto",
            "activity_level": "Alto",
            "restrictions": "Sin gluten",
            "budget": "Moderado",
        }
    )
    assert response.status_code == 200
    assert "html" in response.text.lower()  # Asegura que devuelve una página HTML


