from pydantic import BaseModel, EmailStr
from datetime import datetime


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


"""users scemas"""
class UserBase(BaseModel):
    first_name: str
    last_name: str
    user_email: EmailStr
    org_id: int
    user_password: str
    user_role: str

class CreateUser(UserBase):
    pass

##response model
class UserOut(BaseModel):
    user_id: int
    org_id: int
    first_name: str
    last_name: str
    user_email: str
    user_role: str