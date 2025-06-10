# Service layer for user router
from ..models import db_models
from fastapi import HTTPException, status

def get_users_by_org_id(org_id: int, db):
    """Service function to fetch users by organization id."""
    users = db.query(db_models.Users).filter(db_models.Users.org_id == org_id).all()
    return users


def get_users_by_user_id(user_id: int, db):
    """service function to fetch users by user id"""
    users = db.query(db_models.Users).filter(db_models.Users.user_id == user_id).first()
    return users


def create_user_service(user: 'schemas.CreateUser', db, utils):
    """Service function to create a new user."""
    # if user.user_role == "admin":
    #     return create_user_service_admin(user, db, utils)

    validate_user = db.query(db_models.Users).filter(db_models.Users.user_email == user.user_email).first()
    if validate_user:
        raise Exception("user with email already exists")
    hashed_password = utils.hash(user.user_password)
    user_query = db_models.Users(**user.model_dump())
    user_query.user_password = hashed_password
    validate_org = _validate_organization(user.org_id, db)
    user.org_id = validate_org
    db.add(user_query)
    db.commit()
    db.refresh(user_query)
    return user_query



def create_user_service_admin(user: 'schemas.CreateAdmin', db, utils):
    """Service function to create a new admin_users."""
    validate_user = db.query(db_models.Users).filter(db_models.Users.user_email == user.user_email).first()
    if validate_user:
        raise Exception("user with email already exists")
    hashed_password = utils.hash(user.user_password)
    org_query = db_models.Organizations(org_name = user.org_name,
                                        org_description = user.org_description)
    db.add(org_query)
    db.commit()
    db.refresh(org_query)
    
    org = db.query(db_models.Organizations).filter(db_models.Organizations.org_name == user.org_name).first()
    get_org_id = org.org_id

    user_query = db_models.Users(
                                org_id = get_org_id,
                                first_name = user.first_name,
                                 last_name = user.last_name,
                                 user_email = user.user_email,
                                 user_password = user.user_password,
                                 user_role = user.user_role
                                 )
    
    hashed_password = utils.hash(user.user_password)
    # user_query = db_models.Users(**user.model_dump())
    user_query.user_password = hashed_password

    db.add(user_query)
    db.commit()
    db.refresh(user_query)
    return user_query

def delete_user_service(confirm, db, current_user, utils):
    """Service function to delete a user account after password confirmation."""
    if not utils.verify(confirm.user_password, current_user.user_password):
        raise Exception("Authentication not recognized!!")
    user_query = db.query(db_models.Users).filter(db_models.Users.user_id == current_user.user_id)
    user_query.delete(synchronize_session = False)
    db.commit()
    return True

##helper function to verify organization
def _validate_organization(org: int,  db):
    ##check if user exists
    org_query = db.query(db_models.Organizations).filter(db_models.Organizations.org_id == org).first()
    if not org_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Organization {org} does not exist")
    
    return org