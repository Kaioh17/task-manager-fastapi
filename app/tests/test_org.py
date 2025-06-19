from app.tests.test_db_setup import client, test_org


# Test: Get all organizations

def test_get_all_orgs(test_org):
    response = client.get("/org")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(o["org_id"] == test_org.org_id for o in data)


# Test: Get organization by ID

def test_get_org_by_id(test_org):
    response = client.get(f"/org/{test_org.org_id}")
    assert response.status_code == 202
    data = response.json()
    assert data["org_id"] == test_org.org_id
    assert data["org_name"] == test_org.org_name


# Test: Get organization by invalid ID (should return 404)

def test_get_org_by_invalid_id():
    response = client.get("/org/999999")
    assert response.status_code == 404