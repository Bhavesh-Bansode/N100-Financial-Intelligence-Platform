def test_screener_minimum_roe(client):
    response = client.get("/api/v1/screener?min_roe=15")
    assert response.status_code == 200
    assert all(row["return_on_equity_pct"] >= 15 for row in response.json())


def test_screener_invalid_parameter_returns_400(client):
    assert client.get("/api/v1/screener?min_roe=invalid").status_code == 400
