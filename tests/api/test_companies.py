def test_companies_returns_92_records(client):
    assert len(client.get("/api/v1/companies").json()) == 92


def test_tcs_profile_returns_correct_ticker(client):
    response = client.get("/api/v1/companies/TCS")
    assert response.status_code == 200
    assert response.json()["id"] == "TCS"


def test_invalid_company_returns_404(client):
    assert client.get("/api/v1/companies/INVALID").status_code == 404
