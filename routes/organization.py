from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from dependencies.auth import get_current_user
from models.user import User
from schemas.organization import OrganizationProfileResponse, UpdateOrganizationProfileRequest
from services.organization_service import get_organization_profile, update_organization_profile

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"]
)

@router.get(
    "/profile",
    response_model=OrganizationProfileResponse
)
def organization_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_organization_profile(
        db,
        current_user
    )
    
@router.put("/profile")
def update_profile(
    request: UpdateOrganizationProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_organization_profile(
        db,
        current_user,
        request
    )