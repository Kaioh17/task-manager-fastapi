from app.tests.test_db_setup import client, test_task, test_admin

from app.core.oauth2 import create_access_token

#Test: Create user 
def test_create_task(test_admin):
    token = create_access_token(data={"user_id": test_admin.user_id})
    response = client.post(
            "/task/create",
            headers= {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"                
            },
            json = {
                "task_name": "Hunt Rugarus",
                "task_description": "Downtown newyork||picture of creatures head"
                    }
    )
    assert response.status_code == 201

def test_get_task(test_admin, test_task):
    token = create_access_token(data={"user_id": test_admin.user_id})
    response = client.get(
            "/task",
            headers= {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"                
            }
    )

    assert response.status_code == 200