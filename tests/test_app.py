from app.main import app
from fastapi.testclient import TestClient


def run_tests():
   client = TestClient(app)

   ## Тест 1: Успешное получение Userlist
   print("Тест 1: Успешное получение Userlist...")
   response = client.get("/users/")
   assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
   assert response.json() == {"message": "List of users"}, "Ожидаемый ответ"
   assert response.headers["Content-Type"] == "application/json", "Ожидаемый Content-Type"
   print("Тест 1 пройден успешно!\n")

   # Тест 2: Создание пользователя
   print("Тест 2: Создание пользователя...")
   response = client.post("/users/", json={"username": "test_user"})
   assert response.status_code == 201, f"Ожидался статус 201, получен {response.status_code}"
   assert response.json() == {"message": "User created", "username": "test_user"}
   assert response.headers["Content-Type"] == "application/json", "Ожидаемый Content-Type"
   print("Тест 2 пройден успешно!\n")

   print("Все тесты пройдены успешно!")

if __name__ == "__main__":
    try:
        run_tests()
    except AssertionError as e:
        print(f"Тест не пройден: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")