from fastapi import (APIRouter,Depends, HTTPException,Response,Cookie)
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.auth import (RegisterRequest,VerifyOTPRequest,LoginRequest,ForgotPasswordRequest,VerifyForgotOTPRequest,ResetPasswordRequest,UserResponse) 
from services.auth_service import (logout_user, register_user,login_user,refresh_access_token,forgot_password,verify_forgot_otp,reset_password)
from services.jwt_service import (create_otp_token,decode_token)
from services.auth_service import (verify_otp,resend_otp)
from dependencies.auth import get_current_user
from models.user import User


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post(
    "/register",
    summary="Register User",
    description="Register a new individual or organization account."
)
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

@router.post(
    "/login",
    summary="User Login",
    description="Login using email and password and receive access and refresh tokens in HTTP-only cookies."
    )
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
    
@router.post("/refresh-token")
def refresh_token(
    response: Response,
    refresh_token_cookie: str = Cookie(None),
    db: Session = Depends(get_db)
):

    if not refresh_token_cookie:

        raise HTTPException(
            status_code=401,
            detail="Refresh token missing"
        )

    tokens = refresh_access_token(db,refresh_token_cookie)

    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        samesite="lax",
        secure=False
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        samesite="lax",
        secure=False
    )

    return {
        "message": "Tokens refreshed successfully"
    }
    
@router.post("/logout")
def logout(
    response: Response,
    refresh_token_cookie: str = Cookie(None),
    db: Session = Depends(get_db)
):

    if refresh_token_cookie:
        logout_user(
            db,
            refresh_token_cookie
        )

    response.delete_cookie(
        "access_token"
    )

    response.delete_cookie(
        "refresh_token"
    )

    return {
        "message": "Logout successful"
    }
    
@router.post(
    "/forgot-password",
    summary="Forgot Password",
    description="Send OTP to registered email for password reset."
)
def forgot_password_route(
    request: ForgotPasswordRequest,
    response: Response,
    db: Session = Depends(get_db)
):

    result = forgot_password(
        db,
        request.email
    )

    response.set_cookie(
        key="otp_token",
        value=result["otp_token"],
        httponly=True,
        samesite="lax",
        secure=False
    )

    return {
        "message": result["message"]
    }
    
@router.post("/verify-forgot-otp")
def verify_forgot_password_otp(
    request: VerifyForgotOTPRequest,
    otp_token: str = Cookie(None),
    db: Session = Depends(get_db)
):

    if not otp_token:
        raise HTTPException(
            status_code=401,
            detail="OTP token missing"
        )

    payload = decode_token(otp_token)

    print(payload)
    print(type(payload))
    
    email = payload["email"]
    
    print(email)
    print(type(email))

    return verify_forgot_otp(
        db,
        email,
        request.otp
    )
    
@router.post("/reset-password")
def reset_password_route(
    request: ResetPasswordRequest,
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

    return reset_password(
        db,
        email,
        request.new_password,
        request.confirm_password
    )
    
@router.get(
    "/me",
    response_model=UserResponse
    )
def get_me(
    current_user: User = Depends(get_current_user)
):

    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "account_type": current_user.account_type,
        "is_active": current_user.is_active
    }