def test_health_returns_live_database_counts(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    # The API exposes every user table in the current SQLite database.
    assert len(payload["db_row_counts"]) >= 10
