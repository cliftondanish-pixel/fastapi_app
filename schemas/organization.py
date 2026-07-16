from pydantic import BaseModel
from pydantic import ConfigDict

class OrganizationProfileResponse(BaseModel):
    id: int
    organization_name: str
    status: str
    owner_user_id: int

    class Config:
        model_config = ConfigDict(from_attributes=True)
        
class UpdateOrganizationProfileRequest(BaseModel):
    organization_name: str