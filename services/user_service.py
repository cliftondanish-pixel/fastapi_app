from fastapi import HTTPException
from pytest import Session

from models.user import User
from schemas.user import UpdateProfileRequest

def get_profile(
    current_user: User
):
    return current_user

def update_profile(
    db: Session,
    current_user: User,
    request: UpdateProfileRequest
):

    if request.email != current_user.email:

        existing_user = (
            db.query(User)
            .filter(User.email == request.email)
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

    current_user.full_name = request.full_name
    current_user.email = request.email

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Profile updated successfully"
    }