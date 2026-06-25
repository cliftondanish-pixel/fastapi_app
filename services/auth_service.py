from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.user import User
from models.otp_verification import OTPVerification
from services.otp_service import generate_otp
from services.email_service import send_otp_email
from services.password_service import hash_password
from datetime import datetime, timedelta

def register_user(db:Session,request):
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
        
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )
    db.add(otp_record)
    db.commit()
    
    # print(f"OTP for {request.email}:{otp}")
    send_otp_email(request.email, otp)
    return{"message":"OTP sent successfully"}