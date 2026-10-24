def test_root_returns_running_message(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "FinLens Backend Running"}


def test_protected_endpoint_requires_token(client):
    response = client.get("/investigations/")
    assert response.status_code == 401