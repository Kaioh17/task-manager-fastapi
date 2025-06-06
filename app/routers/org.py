from fastapi import APIRouter, HTTPException, FastAPI, Response,status
from sqlalchemy.orm import Session
from fastapi.params import Depends
from ..models import db_models,schemas
from ..database import get_db
import logging

router = APIRouter(
    prefix = "/org",
    tags = ['Organizations']
)

##get all organizations
@router.get("/", status_code = status.HTTP_200_OK, response_model=list[schemas.OrgOut])
def get_users(db: Session = Depends(get_db)):
    logging.info("Fetching all organizations from the database.")
    org = db.query(db_models.Organizations).all()
    logging.info(f"Fetched {len(org)} organizations.")
    return org


##get organizations by id
@router.get("/{org_id}", status_code=status.HTTP_202_ACCEPTED,response_model=schemas.OrgOut)
def get_user(org_id: int, db: Session = Depends(get_db)):
    logging.info(f"Fetching organization with org_id={org_id}.")
    org = db.query(db_models.Organizations).filter(db_models.Organizations.org_id == org_id).first()
    if not org:
        logging.warning(f"Organization with org_id={org_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization {org_id} not found")
    logging.info(f"Organization with org_id={org_id} found.")
    return org

## add record to organizations
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.OrgOut)
def create_org(org: schemas.CreateOrg, db: Session = Depends(get_db)):
    logging.info(f"Creating organization with name: {org.org_name}")
    org_query = db_models.Organizations(**org.dict())
    db.add(org_query)
    db.commit()
    db.refresh(org_query)
    logging.info(f"Organization created with org_id={org_query.org_id}")
    return org_query