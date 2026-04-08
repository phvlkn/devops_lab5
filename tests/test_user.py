from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

# Существующие пользователи
users = [
    {
        'id': 1,
        'name': 'Ivan Ivanov',
        'email': 'i.i.ivanov@mail.com',
    },
    {
        'id': 2,
        'name': 'Petr Petrov',
        'email': 'p.p.petrov@mail.com',
    }
]

def test_get_existed_user():
    '''Получение существующего пользователя'''
    response = client.get("/api/v1/user", params={'email': users[0]['email']})
    assert response.status_code == 200
    assert response.json() == users[0]

def test_get_unexisted_user():
    '''Получение несуществующего пользователя'''
    response = client.get("/api/v1/user", params={'email': 'no.such.user@mail.com'})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

def test_create_user_with_valid_email():
    '''Создание пользователя с уникальной почтой'''
    payload = {"name": "New User", "email": "new.user.unique@mail.com"}

    # Создаём
    response = client.post("/api/v1/user", json=payload)
    assert response.status_code == 201

    created_id = response.json()
    assert isinstance(created_id, int)
    assert created_id > 0

    # Проверяем, что реально появился
    response_get = client.get("/api/v1/user", params={"email": payload["email"]})
    assert response_get.status_code == 200
    assert response_get.json() == {"id": created_id, **payload}

    # Чистим за собой (чтобы тесты были повторяемыми)
    response_del = client.delete("/api/v1/user", params={"email": payload["email"]})
    assert response_del.status_code == 204

def test_create_user_with_invalid_email():
    '''Создание пользователя с почтой, которую использует другой пользователь'''
    payload = {"name": "Clone", "email": users[0]["email"]}

    response = client.post("/api/v1/user", json=payload)
    assert response.status_code == 409
    assert response.json() == {"detail": "User with this email already exists"}

def test_delete_user():
    '''Удаление пользователя'''
    # Создаём временного пользователя, чтобы не ломать "зашитых"
    payload = {"name": "To Delete", "email": "to.delete.user@mail.com"}

    resp_create = client.post("/api/v1/user", json=payload)
    assert resp_create.status_code == 201
    created_id = resp_create.json()

    # Удаляем
    resp_del = client.delete("/api/v1/user", params={"email": payload["email"]})
    assert resp_del.status_code == 204

    # Проверяем, что больше не существует
    resp_get = client.get("/api/v1/user", params={"email": payload["email"]})
    assert resp_get.status_code == 404
    assert resp_get.json() == {"detail": "User not found"}
