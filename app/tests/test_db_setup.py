from fastapi.testclient import TestClient
from app.models import db_models
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from app.database import get_db,Base
from app.tests.config_test import Settings
from app.utils import hash
settings =Settings()


#In-memory with test_db
SQLALCHEMY_DATABASE_URL = settings.db_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit= False)


#create all tables 
Base.metadata.create_all(bind=engine)

# Dependency override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

db = TestingSessionLocal()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

##fixture to clean db
@pytest.fixture(autouse=True)
def _clean_test_db():
    db = TestingSessionLocal()
    db.query(db_models.Users).delete()
    db.query(db_models.Organizations).delete()
    db.commit()
    db.close()
    

###organizations 
@pytest.fixture
def test_org():
    db = TestingSessionLocal()      
    test_org = db_models.Organizations(org_id = 234, org_name = "Shell",
                                        org_description = "Shell description")
    db.add(test_org)
    db.commit()
    db.refresh(test_org )
    db.close()
    yield test_org

#fixture for user 
@pytest.fixture
def test_user(test_org):
    db = TestingSessionLocal()
    user = db_models.Users(
                        org_id = test_org.org_id, 
                           first_name="Jane", 
                           last_name="Dunner" ,
                           user_email="ihunt@gmail.com",
                           user_password="strongpass1", 
                           user_role = "user"
                           )
    hashed_pwd = hash(user.user_password) 
    user.user_password = hashed_pwd
   
    db.add(user)
    db.commit()
    db.refresh(user)
    

    yield user
    db.close()

@pytest.fixture
def test_admin(test_org):
    db = TestingSessionLocal()

    admin = db_models.Users(
                        org_id = test_org.org_id, 
                           first_name="Sam", 
                           last_name="Winchester" ,
                           user_email="winchester@gmail.com",
                           user_password="strongpass1", 
                           user_role = "admin"
                           )
    hashed_pwd = hash(admin.user_password) 
    admin.user_password = hashed_pwd
   
    db.add(admin)
    db.commit()
    db.refresh(admin)
    

    yield admin
    db.close()

##
@pytest.fixture
def test_task(test_org):
    db = TestingSessionLocal()

    task = db_models.Tasks(
                        org_id = test_org.org_id,
                        task_name = "Hunt Rugarao",
                        task_description = "North Western"
                        )
    db.add(task)
    db.commit()
    db.refresh(task)
    

    yield task
    db.close()