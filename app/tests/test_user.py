from app.tests.test_db_setup import db,client,_clean_test_db,test_org, test_user
from app.models.schemas import UserOut
from app.models import db_models
from app.core.oauth2 import create_access_token
from app.utils import hash, verify
#get user
def test_user_by_id(test_user):
    response = client.get(f"/user/{test_user.user_id}")
    assert response.status_code == 202
    data = response.json()
    assert data["user_email"] == test_user.user_email
    assert data["org_id"] == test_user.org_id


#test create user
def test_create_user(test_org):
    response =  client.post(
        "/user/create",
        headers={"Content-Type": "application/json"},
        json={
                "first_name": "Sam",
                "last_name": "Whinchester",
                "user_email": "ihunt@gmail.com",
                "org_id": "234",
                "user_password": "dean@123",
                "user_role": "admin"
        }
    )
    assert response.status_code == 201


    actual = UserOut(**response.json())

    expected = UserOut(
        user_id=actual.user_id,  # Dynamically set user_id
        org_id="234",
        first_name="Sam",
        last_name="Whinchester",
        user_email="ihunt@gmail.com",
        user_role="admin"
    )

    assert actual == expected  # Compare objects with matching user_id

def test_create_user_duplicate_email(test_user):
    """Test that creating user with duplicate email fails"""
    users = db.query(db_models.Users).all()
    assert len(users) == 1
    assert users[0].user_email == "ihunt@gmail.com"

    print(f"test_email: {users[0].user_email}")
    
    response =  client.post(
        "/user/create",
        headers={"Content-Type": "application/json"},
        json={
                "first_name": "Sam",
                "last_name": "Whinchester",
                "user_email": "ihunt@gmail.com",
                "org_id": "234",
                "user_password": "dean@123",
                "user_role": "admin"
        }
    )
    assert response.status_code == 409  

def test_delete_user(test_user):
    token  = create_access_token(data = {"user_id": test_user.user_id})
    print(f"user_password: {test_user.user_password}")
    response = client.post(
                "/user/delete",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                    },
                json = {
                    "user_password" : "strongpass1"
                }
            )

    assert response.status_code == 204



