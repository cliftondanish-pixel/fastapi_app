from pydantic import BaseModel, EmailStr
from pydantic import ConfigDict

class UserProfileResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    account_type: str
    is_active: bool

    class Config:
        model_config = ConfigDict(from_attributes=True)
        
class UpdateProfileRequest(BaseModel):
    full_name: str
    email: EmailStr