from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta
from core.config import settings
from models.user import User
from services.password_service import verify_password
from services.jwt_service import (create_access_token,create_refresh_token,decode_token,create_otp_token)
from models.refresh_token import RefreshToken
from models.otp_verification import OTPVerification
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
    
    pending_registration = db.query(
        OTPVerification
    ).filter(
        OTPVerification.email == request.email,
        OTPVerification.verified.is_(False),
        OTPVerification.expires_at > datetime.utcnow()
    ).first()
    
    if pending_registration:
        raise HTTPException(
            status_code=400,
            detail="OTP already sent. Please verify or use resend OTP."
    )
    
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400,detail="Passwords do not match")
    
    if request.password != request.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match"
    )
    validate_password(request.password)
    
    hashed_password = hash_password(request.password)
    
    otp = generate_otp()
    otp_record = OTPVerification(
        email=request.email,
        otp=otp,
        purpose="REGISTER",
        
        full_name=request.full_name,
        password_hash=hashed_password,
        account_type=request.account_type,
        organization_name=request.organization_name,
        
        retry_count=0,
        
        expires_at=datetime.utcnow() + timedelta(minutes=settings.OTP_TOKEN_EXPIRE_MINUTES)
    )
    db.add(otp_record)
    db.commit()
    
    # print(f"OTP for {request.email}:{otp}")
    send_otp_email(request.email, otp)
    return {
        "message":"OTP sent successfully"
    }
    
def verify_otp(db:Session,email:str,otp:str):
    otp_record = db.query(OTPVerification).filter(
        OTPVerification.email == email,
        OTPVerification.purpose == "REGISTER",
        OTPVerification.verified.is_(False)
    ).order_by(
        OTPVerification.id.desc()
    ).first()
    
    if not otp_record:
        raise HTTPException(status_code=404,detail="OTP not found")
    
    if otp_record.retry_count >= 5:
        raise HTTPException(status_code=400,detail="Maximum retries exceeded")
    
    if datetime.utcnow() > otp_record.expires_at:
        raise HTTPException(status_code=400,detail="OTP has expired")
    
    if otp_record.otp != otp:
        otp_record.retry_count +=1
        db.commit()
        raise HTTPException(status_code=400,detail="Invalid OTP")
    
    existing_user = db.query(User).filter(
    User.email == email
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )
    
    user = User(
        full_name=otp_record.full_name,
        email=otp_record.email,
        password_hash=otp_record.password_hash,
        account_type=otp_record.account_type,
        is_active=True
    )
    
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    if otp_record.account_type == "Organization":
        tenant = Tenant(
            organization_name=otp_record.organization_name,
            owner_user_id=user.id,
            status="ACTIVE"
        )
        db.add(tenant)
        db.commit()
    otp_record.verified = True 
        
    db.commit()
    return {
            "message":"Account verified successfully"
    }
    
def resend_otp(
    db: Session,
    email: str
):

    otp_record = (
        db.query(OTPVerification)
        .filter(
            OTPVerification.email == email,
            OTPVerification.purpose == "REGISTER",
            OTPVerification.verified.is_(False)
        )
        .order_by(OTPVerification.id.desc())
        .first()
    )

    if not otp_record:
        raise HTTPException(
            status_code=404,
            detail="No pending registration found"
        )
        
    if otp_record.verified:
        raise HTTPException(
            status_code=400,
            detail="Account already verified"
        )

    new_otp = generate_otp()

    otp_record.otp = new_otp
    otp_record.retry_count = 0
    otp_record.expires_at = (
        datetime.utcnow()
        + timedelta(
            minutes=settings.OTP_TOKEN_EXPIRE_MINUTES
        )
    )

    db.commit()

    send_otp_email(email, new_otp)

    return {
        "message": "OTP resent successfully"
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


    refresh_token_record = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    )

    db.add(refresh_token_record)
    db.commit()


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

    # Check token exists in DB
    token_record = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token
    ).first()

    if not token_record:
        raise HTTPException(
            status_code=401,
            detail="Refresh token not found"
        )

    # Check expiry
    if datetime.utcnow() > token_record.expires_at:
        raise HTTPException(
            status_code=401,
            detail="Refresh token expired"
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


    # Delete old refresh token
    db.delete(token_record)


    # Save new refresh token
    new_token_record = RefreshToken(
        user_id=user.id,
        token=new_refresh_token,
        expires_at=datetime.utcnow()
        + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    )

    db.add(new_token_record)
    db.commit()


    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token
    }

def logout_user(
    db: Session,
    refresh_token: str
):

    token_record = db.query(
        RefreshToken
    ).filter(
        RefreshToken.token == refresh_token
    ).first()


    if token_record:
        db.delete(token_record)
        db.commit()


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

    otp_record = OTPVerification(
        email=email,
        otp=otp,
        purpose="FORGOT_PASSWORD",
        retry_count=0,
        expires_at=datetime.utcnow() + timedelta(minutes=settings.OTP_TOKEN_EXPIRE_MINUTES)      
    )

    db.add(otp_record)
    db.commit()

    send_otp_email(email, otp)

    otp_token = create_otp_token(email)

    return {
        "message": "OTP sent successfully",
        "otp_token": otp_token
    }
    
def verify_forgot_otp(
    db: Session,
    email: str,
    otp: str
):

    otp_record = (
        db.query(OTPVerification)
        .filter(
            OTPVerification.email == email,
            OTPVerification.purpose == "FORGOT_PASSWORD",
            OTPVerification.verified == False
        )
        .order_by(OTPVerification.id.desc())
        .first()
    )

    if not otp_record:
        raise HTTPException(
            status_code=404,
            detail="OTP not found"
        )

    if otp_record.retry_count >= 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum retries exceeded"
        )

    if datetime.utcnow() > otp_record.expires_at:
        raise HTTPException(
            status_code=400,
            detail="OTP has expired"
        )

    if otp_record.otp != otp:

        otp_record.retry_count += 1
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    otp_record.verified = True
    db.commit()

    return {
        "message": "OTP verified successfully"
    }
    
def reset_password(
    db: Session,
    email: str,
    password: str,
    confirm_password: str
):

    if password != confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match"
        )

    validate_password(password)

    # Get latest verified forgot-password OTP
    otp_record = (
        db.query(OTPVerification)
        .filter(
            OTPVerification.email == email,
            OTPVerification.purpose == "FORGOT_PASSWORD",
            OTPVerification.verified == True
        )
        .order_by(OTPVerification.id.desc())
        .first()
    )

    if not otp_record:
        raise HTTPException(
            status_code=400,
            detail="OTP verification required"
        )

    # Find user
    user = (
        db.query(User)
        .filter(User.email == email)
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

