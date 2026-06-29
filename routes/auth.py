from fastapi import (APIRouter,Depends, HTTPException,Response,Cookie)
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.auth import (RegisterRequest,VerifyOTPRequest,LoginRequest) 
from services.auth_service import (register_user,login_user)
from services.jwt_service import (create_otp_token,decode_token)
from services.auth_service import (verify_otp,resend_otp)


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
    if not otp_token:

        raise HTTPException(
            status_code=401,
            detail="OTP token missing"
        )


    payload = decode_token(
        otp_token
    )

    email = payload["email"]


    return verify_otp(
        db,
        email,
        request.otp
    )
    
@router.post("/resend-otp")
def resend_user_otp(
    otp_token: str = Cookie(None),
    db: Session = Depends(get_db)
):

    if not otp_token:
        raise HTTPException(
            status_code=401,
            detail="OTP token missing"
        )

    payload = decode_token(otp_token)

    email = payload["email"]

    return resend_otp(db, email)

@router.post("/login")
def login(
    request: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):

    result = login_user(
        db,
        request
    )


    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        samesite="lax",
        secure=False   # True in production
    )


    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        samesite="lax",
        secure=False
    )


    return {
        "message": result["message"]
    }