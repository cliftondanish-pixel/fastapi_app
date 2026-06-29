from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta
from core.config import settings
from models.user import User
from models.otp_verification import OTPVerification
from services.otp_service import generate_otp
from services.email_service import send_otp_email
from services.password_service import hash_password
from models.tenant import Tenant
from schemas.auth import RegisterRequest


def register_user(db:Session,request:RegisterRequest):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400,detail="Email already registered")
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400,detail="Passwords do not match")
    
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
    

    