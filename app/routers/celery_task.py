from sqlalchemy.orm import Session
from fastapi.params import Depends
from ..database import  SessionLocal
from ..models import db_models
from ..core.celery_worker import celery_app
from fastapi import HTTPException, status
import logging
from types import SimpleNamespace
from datetime import datetime

# Set up logging for better debugging
logger = logging.getLogger(__name__)

##db_models configuration
TABLE_MODEL_MAPPING = {
    'task_assignment': {
        'model':db_models.TaskAssignment,
        'primary_key': 'assignment_id'
    },
    'audit_log': {
        'model':db_models.AuditLog,
        'primary_key': 'assignment_id',
        'columns': {
                    'assignment_id', 
                    'task_id',
                    'org_id',
                    'user_id',
                    'task_name',
                    'task_description',
                    'task_status',
                    'proof_of_completion',                   
                    'assigned_on'
                    }
    },
    'approved_task_archives': {
        'model':db_models.ApprovedTaskArchive,
        'primary_key': 'assignment_id',
        'columns': [
                    'assignment_id', 
                    'task_id',
                    'org_id',
                    'user_id',
                    'task_name',
                    'task_description',
                    'task_status',
                    'proof_of_completion',  
                    'completed_on', 
                    'approved_by',                
                    'assigned_on',
                    ]
    }
}

@celery_app.task(bind=True)
def delete_row(self, table_name:str, row_id: int):
    """
    Delete a TaskAssignment row after a delay.
    Using bind=True to access task instance for better error handling.
    """
    db = None
    try:
        logger.info(f"Starting deletion task for row_id: {row_id} table: {table_name}")
        db = SessionLocal()

        #get model and primary key info
        table_info = TABLE_MODEL_MAPPING[table_name]
        model_class = table_info['model']
        primary_key_column = table_info['primary_key']
        
        print(model_class)
        # Query the row
        row = db.query(model_class).filter(
            getattr(model_class, primary_key_column) == row_id
        ).first()
        
        if row:
            db.delete(row)
            db.commit()
            logger.info(f"Successfully deleted row with id: {row_id}")
            return f"Row {row_id} deleted successfully"
        else:
            logger.warning(f"Row with id {row_id} not found")
            return f"Row {row_id} not found"
            
    except Exception as exc:
        logger.error(f"Error deleting row {row_id}: {str(exc)}")
        if db:
            db.rollback()
        # Retry the task up to 3 times with exponential backoff
        raise self.retry(exc=exc, countdown=60, max_retries=3)
    finally:
        if db:
            db.close()

@celery_app.task(bind=True)
def add_rows(self,table_name:str, assignment_dict: dict):
    """add row after a delay"""
    db = None
    try:
        logger.info(f"Adding task to the {table_name}")
        db = SessionLocal()

        #get
        table_info = TABLE_MODEL_MAPPING[table_name]
        model_class = table_info['model']
        columns = table_info['columns']

        # Convert string datetimes to datetime objects for known datetime fields
        cleaned_data = {key: assignment_dict[key] for key in columns if key in assignment_dict}
        
        logger.info(f"Data align")
        new_row = model_class(**cleaned_data)
        db.add(new_row)
        db.commit()
        logger.info(f"Task has been added as row")
    except Exception as exc:
        logger.error(f"Error adding row to {table_name}: {str(exc)}")
        # if db:
        #     db.rollback()
        # raise self.retry(exc=exc, countdown=60, max_retries=3)
    finally:
        if db:
            db.close()