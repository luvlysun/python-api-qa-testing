import pytest

from app import create_app


@pytest.fixture
def client():
    return create_app().test_client()


def test_creates_order(client):
    response = client.post("/orders", json={"quantity": 2})

    assert response.status_code == 201
    assert response.json == {"id": 1, "quantity": 2}


def test_rejects_zero_quantity(client):
    response = client.post("/orders", json={"quantity": 0})

    assert response.status_code == 400


def test_retry_returns_original_order(client):
    headers = {"Idempotency-Key": "order-123"}
    payload = {"quantity": 2}

    first = client.post("/orders", json=payload, headers=headers)
    retry = client.post("/orders", json=payload, headers=headers)

    assert first.status_code == 201
    assert retry.json["id"] == first.json["id"]

def test_rejects_same_key_with_different_quantity(client):
    headers = {"Idempotency-Key": "order-123"}

    first = client.post(
        "/orders",
        json={"quantity": 2},
        headers=headers
    )

    second = client.post(
        "/orders",
        json={"quantity": 5},
        headers=headers
    )

    assert first.status_code == 201
    assert second.status_code == 409