from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from dependencies.auth import get_current_user
from models.user import User
from schemas.user import UpdateProfileRequest, UserProfileResponse
from services.user_service import get_profile, update_profile

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get(
    "/profile",
    response_model=UserProfileResponse
)
def profile(
    current_user: User = Depends(get_current_user)
):
    return get_profile(current_user)

@router.put("/profile")
def update_user_profile(
    request: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_profile(
        db,
        current_user,
        request
    )