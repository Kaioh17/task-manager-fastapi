from app.tests.test_db_setup import client,_clean_test_db,test_org, test_user
from app.models.schemas import UserOut
from app.core.oauth2 import create_access_token
from app.utils import hash, verify


def test_create_org():

    response = client.post(
                "/org",
                 headers={"Content-Type": "application/json"},
                 json = {
                     "org_name": "Hunters Association",
                     "org_description": "Hunt and kill monsters. Responsible for Journaling lores "
                 }
    )

    response.status_code == 201

    