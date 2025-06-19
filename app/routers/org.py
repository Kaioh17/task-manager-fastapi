from fastapi import APIRouter, HTTPException, FastAPI, Response,status
from sqlalchemy.orm import Session
from fastapi.params import Depends
from ..models import db_models,schemas
from ..database import get_db
import logging
from app.services import org_service
router = APIRouter(
    prefix = "/org",
    tags = ['Organizations']
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

##get all organizations
@router.get("/", status_code = status.HTTP_200_OK, response_model=list[schemas.OrgOut])
def get_org(db: Session = Depends(get_db)):
    logger.info("Fetching all organizations from the database.")
    org = org_service.get_organizations(db)
    logger.info(f"Fetched {len(org)} organizations.")
    return org


##get organizations by id
@router.get("/{org_id}", status_code=status.HTTP_202_ACCEPTED,response_model=schemas.OrgOut)
def get_org_id(org_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching organization with org_id={org_id}.")
    org = org_service.get_organization_by_id(org_id, db)
    if not org:
        logger.warning(f"Organization with org_id={org_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Organization {org_id} not found")
    logger.info(f"Organization with org_id={org_id} found.")
    return org
