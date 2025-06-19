from app.tests.test_db_setup import client, test_org


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
