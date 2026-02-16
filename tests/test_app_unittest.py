from fastapi.testclient import TestClient
from app.main import app
import unittest


class TestUserAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_get_users(self):
        response = self.client.get("/users/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "List of users"})
        self.assertEqual(response.headers["Content-Type"], "application/json")


    def test_create_user(self):
        response = self.client.post("/users/", json={"username": "John Doe"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"message": "User created", "username": "John Doe"})
        self.assertEqual(response.headers["Content-Type"], "application/json")


if __name__ == "__main__":
    unittest.main()
