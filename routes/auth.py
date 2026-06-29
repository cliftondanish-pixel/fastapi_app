from fastapi import (APIRouter,Depends,Response,Cookie)
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.auth import (RegisterRequest,VerifyOTPRequest)
from services.auth_service import register_user
from services.jwt_service import (create_otp_token,decode_token)
from services.auth_service import verify_otp


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register")
def register(
    request: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db)
):

    result = register_user(db,request)
    otp_token = create_otp_token(request.email)
    response.set_cookie(
        key="otp_token",
        value=otp_token,
        httponly=True,
        samesite="lax"
    )

    return result

@router.post("/verify-otp")
def verify_user_otp(
    request: VerifyOTPRequest,
    otp_token: str = Cookie(None),
    db:Session = Depends(get_db)
):