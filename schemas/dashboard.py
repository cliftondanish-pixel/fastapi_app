from pydantic import BaseModel

class IndividualDashboardResponse(BaseModel):
    full_name: str
    email: str
    account_type: str
    is_active: bool

class OrganizationDashboardResponse(BaseModel):
    organization_name: str
    total_users: int
    active_users: int
    inactive_users: int
    status: str