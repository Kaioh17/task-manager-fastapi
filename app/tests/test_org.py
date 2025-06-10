from app.tests.test_db_setup import client,_clean_test_db,test_org, test_user
from app.models.schemas import UserOut
from app.core.oauth2 import create_access_token
from app.utils import hash, verify


# Test: Create organization

def test_create_org():
    response = client.post(
        "/org",
        headers={"Content-Type": "application/json"},
        json={
            "org_name": "Hunters Association",
            "org_description": "Hunt and kill monsters. Responsible for Journaling lores "
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["org_name"] == "Hunters Association"
    assert data["org_description"].startswith("Hunt and kill")


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


# Test: Create organization with missing fields (should return 422)

def test_create_org_missing_fields():
    response = client.post(
        "/org",
        headers={"Content-Type": "application/json"},
        json={
            "org_description": "Missing name"
        }
    )
    assert response.status_code == 422