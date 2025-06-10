from app.tests.test_db_setup import db,client,_clean_test_db,test_org, test_user
from app.models.schemas import UserOut
from app.models import db_models
from app.core.oauth2 import create_access_token
from app.utils import hash, verify

# # Test: Get user by ID
# def test_user_by_id(test_user):
#     response = client.get(f"/user/{test_user.user_id}")
#     assert response.status_code == 202
#     data = response.json()
#     assert data["user_email"] == test_user.user_email
#     assert data["org_id"] == test_user.org_id


# Test: Create user
def test_create_user(test_org):
    response =  client.post(
        "/user/create/user",
        headers={"Content-Type": "application/json"},
        json={
                "first_name": "Sam", 
                "last_name": "Whinchester",
                "user_email": "ihunt@gmail.com",
                "org_id": "234",
                "user_password": "dean@123",
                "user_role": "user"
        }
    )
    assert response.status_code == 201


    # actual = UserOut(**response.json())

    # expected = UserOut(
    #     user_id=actual.user_id,  # Dynamically set user_id
    #     org_id="234",
    #     first_name="Sam",
    #     last_name="Whinchester",
    #     user_email="ihunt@gmail.com",
    #     user_role="user"
    # )

    # assert actual == expected  # Compare objects with matching user_id


# Test: Create admin
def test_create_admin(test_org):
    response =  client.post(
        "/user/create/admin",
        headers={"Content-Type": "application/json"},
        json={
                "first_name": "Sam", 
                "last_name": "Whinchester",
                "user_email": "ihunt@gmail.com",
                "user_password": "dean@123",
                "user_role": "admin",
                "org_name": "some org",
                "org_description": "track down the mossad"
        }
    )
    assert response.status_code == 201


    # actual = UserOut(**response.json())

    # expected = UserOut(
    #     user_id=actual.user_id,  # Dynamically set user_id
    #     org_id="234",
    #     first_name="Sam",
    #     last_name="Whinchester",
    #     user_email="ihunt@gmail.com",
    #     user_role="admin"
    # )

    # assert actual == expected  # Compare objects with matching user_id


# Test: Create user with duplicate email
def test_create_user_duplicate_email(test_user):
    """Test that creating user with duplicate email fails"""
    users = db.query(db_models.Users).all()
    assert len(users) == 1
    assert users[0].user_email == "ihunt@gmail.com"

    print(f"test_email: {users[0].user_email}")
    
    response =  client.post(
        "/user/create/user",
        headers={"Content-Type": "application/json"},
        json={
                "first_name": "Sam",
                "last_name": "Whinchester",
                "user_email": "ihunt@gmail.com",
                "org_id": "234",
                "user_password": "dean@123",
                "user_role": "user"
        }
    )
    assert response.status_code == 409  

# Test: Delete user
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


# Test: Get user by invalid ID (should return 404)
def test_get_user_by_invalid_id():
    response = client.get("/user/999999")
    assert response.status_code == 404


# Test: Create user with missing required fields (should return 422)
def test_create_user_missing_fields():
    response = client.post(
        "/user/create/user",
        headers={"Content-Type": "application/json"},
        json={
            "first_name": "NoLastName",
            "user_email": "missing@fields.com",
            "org_id": "234",
            "user_password": "testpass",
            "user_role": "user"
        }
    )
    assert response.status_code == 422


# Test: Delete user with wrong password (should return 401)
def test_delete_user_wrong_password(test_user):
    token = create_access_token(data={"user_id": test_user.user_id})
    response = client.post(
        "/user/delete",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={"user_password": "wrongpassword"}
    )
    assert response.status_code == 401


# Test: Get users by invalid organization (should return 404)
# def test_get_users_by_invalid_org(test_user):

#     token = create_access_token(data={"user_id": test_user.user_id})
#     response = client.get(
#         "/user/organization/999999",
#         headers={
#             "Authorization": f"Bearer {token}"
#         }
        
#         )
#     assert response.status_code == 404



