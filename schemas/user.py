from pydantic import BaseModel, EmailStr

class UserProfileResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    account_type: str
    is_active: bool

    class Config:
        from_attributes = True
        
class UpdateProfileRequest(BaseModel):
    full_name: str
    email: EmailStr