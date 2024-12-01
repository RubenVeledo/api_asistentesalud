import pytest
from fastapi.testclient import TestClient
from app.main import app


# Crear un cliente de pruebas para FastAPI
client = TestClient(app)

@pytest.fixture
def test_client():
    """Fixture para usar el cliente de pruebas"""
    return client


# Test para el endpoint de la página principal
def test_home_endpoint(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert "Salus AI" in response.text


# Test para el endpoint de /routine
def test_routine_endpoint(test_client):
    response = test_client.post(
        "/routine",
        data={
            "level": "Intermedio",
            "time": 60,
            "equipment": "Mancuernas",
            "goal": "Ganar músculo",
        },
    )
    assert response.status_code == 200
    assert "Generada con éxito" in response.text or "Rutina personalizada" in response.text


# Test para el endpoint de /dieta
def test_dieta_endpoint(test_client):
    response = test_client.post(
        "/dieta",
        data={
            "goal": "Perder peso",
            "preferences": "Sin gluten, Sin lactosa",
        },
    )
    assert response.status_code == 200
    assert "Dieta personalizada" in response.text or "Generada con éxito" in response.text


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
        },
    )
    assert response.status_code == 200
    assert "Recomendaciones generadas con éxito" in response.text or "Nombre del suplemento" in response.text
