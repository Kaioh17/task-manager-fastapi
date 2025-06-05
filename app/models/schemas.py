from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from fastapi import File, UploadFile,Form


"""Organizations schemas"""
class OrgBase(BaseModel):
    org_name: str
    org_description: str

class CreateOrg(OrgBase):
    pass
    model_config = {"from_attributes": True}
 ##response model 
class OrgOut(OrgBase):
    org_id: int
    model_config = {"from_attributes": True}


"""users schemas"""
class UserBase(BaseModel):
    first_name: str
    last_name: str
    user_email: EmailStr
    org_id: int
    user_password: str
    user_role: str

class CreateUser(UserBase):
    pass

class DeleteUser(BaseModel):
    user_password : str

##response model
class UserOut(BaseModel):
    user_id: int
    org_id: int
    first_name: str
    last_name: str
    user_email: str
    user_role: str

"""login schemas"""
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None


"""tasks schemas"""
class TaskBase(BaseModel):
    # org_id: int
    task_name: str
    task_description: str
   
    # created_on: datetime
class TaskOut(BaseModel):
    task_id: int
    org_id: int
    task_name: str
    task_description: str

"""Assigning task"""
class AssignTaskBase(BaseModel):
    task_id: int
    user_id: int
    due_date: datetime # expects format: "2025-06-01T15:30:00"

class AssignTask(AssignTaskBase):
    pass
class StatusUpdate(BaseModel):
    task_status: str = Form(...)
    proof_of_completion: Optional[UploadFile] = File(None)
class Approved(BaseModel):
     assignment_id: int


class AssignedTaskOut(BaseModel):
    assignment_id: int
    task_id: int
    org_id: int
    user_id: int
    task: TaskOut
    due_date: datetime
