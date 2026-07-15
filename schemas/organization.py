from pydantic import BaseModel

class OrganizationProfileResponse(BaseModel):
    id: int
    organization_name: str
    status: str
    owner_user_id: int

    class Config:
        from_attributes = True
        
class UpdateOrganizationProfileRequest(BaseModel):
    organization_name: str