from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from fastapi import File, UploadFile,Form
from typing import Literal


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

"""organiztion settings (admin only)"""

class SettingsPayload(BaseModel):
    manager_clearance: Literal["high", "medium", "low"]
    # theme: Literal["light", "dark"]

class org_settings(BaseModel):
    settings: SettingsPayload

"""admin"""
class PromoteUser(BaseModel):
    user_role: str = "manager"



"""users schemas"""
class UserBase(BaseModel):
    first_name: str
    last_name: str
    user_email: EmailStr
    user_password: str =Field(min_length=8)
    
class CreateUser(UserBase):
    org_id: int
    org_token: str
    user_role: str = Field(pattern="^(user)$")

class CreateAdmin(UserBase):
    user_role: str = Field(pattern="^(admin)$")
    org_name: str
    org_description: str
    
class UpdateAdmin(UserBase):
    org_name: str
    org_description: str
class DeleteUser(BaseModel):
    user_password : str

##response model
class UserOut(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    user_email: str
    user_role: str
    organization: OrgOut
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
    task_status: str = Form(...), Field()
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

class DeletedResponse(BaseModel):
    organization: OrgOut
    user_id: int
    users: UserOut
    model_config = {"from_attributes": True}
