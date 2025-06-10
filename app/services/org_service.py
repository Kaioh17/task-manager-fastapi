# Service layer for org router
from ..models import db_models
from fastapi import HTTPException, status

def get_organizations(db):
    org = db.query(db_models.Organizations).all()   
    return org

def get_organization_by_id(org_id: int, db):
    org = db.query(db_models.Organizations).filter(db_models.Organizations.org_id == org_id).first()
    return org

def create_organization(org, db):
    org_query = db_models.Organizations(**org.model_dump())
    
    db.add(org_query)
    db.commit()
    db.refresh(org_query)
    return org_query
