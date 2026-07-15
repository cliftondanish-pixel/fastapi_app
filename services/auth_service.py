from sqlalchemy.orm import Session
from fastapi import HTTPException
# from datetime import datetime, timedelta, UTC
# from core.config import settings
from models.user import User
from services.password_service import verify_password
from services.jwt_service import (create_access_token,create_refresh_token,decode_token,create_otp_token)
from services.otp_service import generate_otp
from services.email_service import send_otp_email
from services.password_service import (hash_password,validate_password)
from models.tenant import Tenant
from schemas.auth import (RegisterRequest,LoginRequest)
from services.email_validation_service import (is_personal_email,is_business_email)


def register_user(db:Session,request:RegisterRequest):
    
    if request.account_type == "Individual":

        if not is_personal_email(request.email):
            raise HTTPException(
                status_code=400,
                detail="Individual accounts must use a personal email address"
            )

    elif request.account_type == "Organization":

        if not request.organization_name:
            raise HTTPException(
                status_code=400,
                detail="Organization name is required"
            )

        if not is_business_email(request.email):
            raise HTTPException(
                status_code=400,
                detail="Organization accounts must use an official business email"
            )

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid account type"
        )

    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400,detail="Email already registered")
    
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400,detail="Passwords do not match")
    
    validate_password(request.password)
    
    hashed_password = hash_password(request.password)
    
    otp = generate_otp()

    otp_payload = {
        "email": request.email,
        "otp": otp,
        "purpose": "REGISTER",
        "full_name": request.full_name,
        "password_hash": hashed_password,
        "account_type": request.account_type,
        "organization_name": request.organization_name,
        "retry_count": 0

    }

    otp_token = create_otp_token(otp_payload)

    send_otp_email(request.email, otp)

    return {
        "message": "OTP sent successfully",
        "otp_token": otp_token
    }
    # print(f"OTP for {request.email}:{otp}")
    
def verify_otp(db: Session,payload: dict,otp: str):  
    
    if payload.get("retry_count", 0) >= 5:
        raise HTTPException(status_code=400,detail="Maximum retries exceeded")
    
    # print("Current local time:", datetime.now())
    # print("Current UTC time:", datetime.utcnow())
    # print("Expires at:", otp_record.expires_at)
    
    if payload["otp"] != otp:
        raise HTTPException(status_code=400,detail="Invalid OTP")
    
    existing_user = db.query(User).filter(
    User.email == payload["email"]
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )
    
    user = User(
        full_name=payload["full_name"],
        email=payload["email"],
        password_hash=payload["password_hash"],
        account_type=payload["account_type"],
        is_active=True
    )
    
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    if payload["account_type"] == "Organization":
        tenant = Tenant(
            organization_name=payload["organization_name"],
            owner_user_id=user.id,
            status="ACTIVE"
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        user.tenant_id = tenant.id
        db.commit()
        
    return {
            "message":"Account verified successfully"
    }
    
def resend_otp(payload: dict):

    new_otp = generate_otp()

    payload["otp"] = new_otp
    payload["retry_count"] = 0

    new_token = create_otp_token(payload)

    send_otp_email(payload["email"], new_otp)

    return {
        "message": "OTP resent successfully",
        "otp_token": new_token
    }
    
def login_user(
    db: Session,
    request: LoginRequest
):

    user = db.query(User).filter(
        User.email == request.email
    ).first()


    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )


    if not verify_password(
        request.password,
        user.password_hash
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )


    if not user.is_active:

        raise HTTPException(
            status_code=403,
            detail="Account is not active"
        )


    access_token = create_access_token(
        {
            "user_id": user.id,
            "email": user.email
        }
    )


    refresh_token = create_refresh_token(
        {
            "user_id": user.id
        }
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token
    }
    
def refresh_access_token(
    db: Session,
    refresh_token: str
):

    # Verify JWT
    payload = decode_token(refresh_token)

    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    # Get user
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Create new access token
    access_token = create_access_token(
        {
            "user_id": user.id,
            "email": user.email
        }
    )
    
    # Create NEW refresh token
    new_refresh_token = create_refresh_token(
        {
            "user_id": user.id
        }
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token
    }

def logout_user(
    db: Session,
    refresh_token: str
):
    return {
        "message": "Logout successful"
    }
def forgot_password(
    db: Session,
    email: str
):

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    otp = generate_otp()

    payload = {
        "email": email,
        "otp": otp,
        "purpose": "FORGOT_PASSWORD",
        "retry_count": 0
    }
    
    otp_token = create_otp_token(payload)
    send_otp_email(email, otp)

    return {
        "message": "OTP sent successfully",
        "otp_token": otp_token
    }
    
def verify_forgot_otp(
    payload: dict,
    otp: str
):

    if payload.get("retry_count", 0) >= 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum retries exceeded"
        )

    if payload["purpose"] != "FORGOT_PASSWORD":
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP token"
        )

    payload["verified"] = True
    new_token = create_otp_token(payload)

    return {
        "message": "OTP verified successfully",
        "otp_token": new_token
    }
    
def reset_password(
    db: Session,
    payload: dict,
    password: str,
    confirm_password: str
):

    if password != confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match"
        )

    validate_password(password)
    
    if payload.get("purpose") != "FORGOT_PASSWORD":
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP token"
        )

    if not payload.get("verified"):
        raise HTTPException(
            status_code=400,
            detail="OTP verification required"
        )

    # Find user
    user = (
        db.query(User)
        .filter(User.email == payload["email"])
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Update password
    user.password_hash = hash_password(password)
    db.commit()

    return {
        "message": "Password reset successful"
    }

