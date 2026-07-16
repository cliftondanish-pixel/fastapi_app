from pydantic import BaseModel, EmailStr
from pydantic import ConfigDict

class CreateTenantUserRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    confirm_password: str
    
class TenantUserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    account_type: str
    is_active: bool

    class Config:
        model_config = ConfigDict(from_attributes=True)
        
class UpdateTenantUserRequest(BaseModel):
    full_name: str
    email: EmailStr
    
class UpdateUserStatusRequest(BaseModel):
    is_active: bool