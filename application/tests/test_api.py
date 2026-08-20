from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

def test_version():
    response = client.get("/version")

    assert response.status_code == 200

    data = response.json()

    assert data["application"] == "Order Management API"
    assert data["version"] == "1.0.0"

def test_invalid_order():

    payload = {
        "customer_name": "",
        "product_name": "Laptop",
        "quantity": -1,
        "price": -100,
    }

    response = client.post("/orders", json=payload)

    assert response.status_code == 422


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_readiness():
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_create_order():

    payload = {
        "customer_name": "Test User",
        "product_name": "Laptop",
        "quantity": 1,
        "price": 1000,
    }

    response = client.post("/orders", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["customer_name"] == "Test User"
    assert data["product_name"] == "Laptop"
    assert data["quantity"] == 1
    assert data["price"] == 1000
    assert data["status"] == "CREATED"
    assert "order_id" in data


def test_get_nonexistent_order():

    response = client.get("/orders/non-existent-id")

    assert response.status_code == 404