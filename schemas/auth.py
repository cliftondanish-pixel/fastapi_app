from typing import Literal, Optional
from pydantic import (BaseModel, EmailStr, field_validator,ConfigDict)

class RegisterRequest(BaseModel):
    full_name:str
    email: EmailStr
    password: str
    confirm_password:str
    account_type: Literal["Individual", "Organization"]
    organization_name: Optional[str] = None
    
    @field_validator("password")
    @classmethod
    def validate_password(cls,value):
        if len(value)<8:
            raise ValueError("Password must be at least 8 characters long")
        return value
    
    @field_validator("organization_name")
    @classmethod
    def validate_organization_name(cls,value,info):
        account_type=info.data.get("account_type")
        if(account_type == "Organization" and not value):
            raise ValueError("Organization name is required")
        return value
    
class VerifyOTPRequest(BaseModel):
    otp:str
        
class LoginRequest(BaseModel):
    email:EmailStr
    password:str
        
class ForgotPasswordRequest(BaseModel):
    email:EmailStr
        
class VerifyForgotOTPRequest(BaseModel):
    otp: str
        
class ResetPasswordRequest(BaseModel):
    new_password:str
    confirm_password:str

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    account_type: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)