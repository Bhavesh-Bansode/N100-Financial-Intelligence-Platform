def test_sectors_returns_all_live_sectors(client):
    response = client.get("/api/v1/sectors")
    assert response.status_code == 200
    # Source data currently contains ten distinct broad sectors.
    assert len(response.json()) == 10


def test_information_technology_sector_companies_are_consistent(client):
    response = client.get("/api/v1/sectors/Information%20Technology/companies")
    assert response.status_code == 200
    assert all(row["broad_sector"] == "Information Technology" for row in response.json())
