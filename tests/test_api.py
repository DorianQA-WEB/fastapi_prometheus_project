from fastapi.testclient import TestClient

def test_get_users(client: TestClient):
    response = client.get("/users/")
    assert response.status_code == 200
    assert response.json() == {"message": "List of users"}
    assert response.headers["Content-Type"] == "application/json"

def test_create_user(client: TestClient, test_user, setup_and_teardown):
    response = client.post("/users/", json=test_user)
    assert response.status_code == 201
    assert response.json() == {"message": "User created", "username": "John Doe"}
    assert "application/json" in response.headers["Content-Type"]


def test_create_user_shot_username(client: TestClient, test_user, setup_and_teardown):
    response = client.post("/users/", json=test_user)
    assert response.status_code == 400
    assert response.json() == {"detail": "Username is too short"}
    assert "application/json" in response.headers["Content-Type"]
