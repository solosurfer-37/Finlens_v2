def bad_upload(client, headers, csv_bytes):
    return client.post(
        "/upload/",
        headers=headers,
        files={"file": ("bad.csv", csv_bytes, "text/csv")},
    )


def test_missing_columns_returns_400(client, auth_headers):
    headers = auth_headers("bad1@finlens.com")
    response = bad_upload(client, headers, b"foo,bar\n1,2\n")
    assert response.status_code == 400


def test_invalid_amount_returns_400(client, auth_headers, sample_csv):
    headers = auth_headers("bad2@finlens.com")
    bad = sample_csv.replace(b"1200000", b"abc")
    response = bad_upload(client, headers, bad)
    assert response.status_code == 400


def test_bad_upload_leaves_no_orphan_investigation(client, auth_headers):
    headers = auth_headers("bad3@finlens.com")
    bad_upload(client, headers, b"foo,bar\n1,2\n")
    assert client.get("/investigations/", headers=headers).json() == []