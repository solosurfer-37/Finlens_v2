import pytest


def upload(client, headers, csv_bytes):
    return client.post(
        "/upload/",
        headers=headers,
        files={"file": ("data.csv", csv_bytes, "text/csv")},
    )


@pytest.fixture
def owned_investigation(client, auth_headers, sample_csv):
    owner = auth_headers("owner@finlens.com")
    other = auth_headers("other@finlens.com")
    response = upload(client, owner, sample_csv)
    assert response.status_code == 200
    return response.json()["investigation_id"], owner, other


def test_owner_can_read_own_investigation(client, owned_investigation):
    inv_id, owner, _ = owned_investigation
    assert client.get(f"/investigations/{inv_id}", headers=owner).status_code == 200


def test_other_user_cannot_read_investigation(client, owned_investigation):
    inv_id, _, other = owned_investigation
    assert client.get(f"/investigations/{inv_id}", headers=other).status_code == 404


def test_other_user_cannot_read_evidence(client, owned_investigation):
    inv_id, owner, other = owned_investigation
    assert client.get(f"/investigations/{inv_id}/evidence", headers=owner).status_code == 200
    assert client.get(f"/investigations/{inv_id}/evidence", headers=other).status_code == 404


def test_other_user_cannot_read_cached_graph(client, owned_investigation):
    inv_id, owner, other = owned_investigation
    assert client.get(f"/investigations/{inv_id}/graph", headers=owner).status_code == 200
    assert client.get(f"/investigations/{inv_id}/graph", headers=other).status_code == 404


def test_other_user_cannot_read_cached_report(client, owned_investigation):
    inv_id, owner, other = owned_investigation
    assert client.get(f"/investigations/{inv_id}/report", headers=owner).status_code == 200
    assert client.get(f"/investigations/{inv_id}/report", headers=other).status_code == 404


def test_list_only_shows_own_investigations(client, owned_investigation):
    inv_id, owner, other = owned_investigation
    owner_ids = [i["id"] for i in client.get("/investigations/", headers=owner).json()]
    other_ids = [i["id"] for i in client.get("/investigations/", headers=other).json()]
    assert inv_id in owner_ids
    assert other_ids == []