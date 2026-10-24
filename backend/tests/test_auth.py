USER = {"email": "auth_test@finlens.com", "password": "StrongPass123"}


def register(client, payload=USER):
    return client.post("/auth/register", json=payload)


def login(client, payload=USER):
    return client.post("/auth/login", json=payload)


def test_register_success_hides_password(client):
    response = register(client)
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == USER["email"]
    assert "id" in body
    assert "hashed_password" not in body
    assert "password" not in body


def test_register_duplicate_email_rejected(client):
    register(client)
    response = register(client)
    assert 400 <= response.status_code < 500


def test_login_success_returns_token(client):
    register(client)
    response = login(client)
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password_returns_401(client):
    register(client)
    response = login(client, {"email": USER["email"], "password": "WrongPass999"})
    assert response.status_code == 401


def test_login_unknown_email_same_error_as_wrong_password(client):
    register(client)
    wrong_pw = login(client, {"email": USER["email"], "password": "WrongPass999"})
    unknown = login(client, {"email": "nobody@finlens.com", "password": "WrongPass999"})
    assert unknown.status_code == wrong_pw.status_code == 401
    assert unknown.json() == wrong_pw.json()