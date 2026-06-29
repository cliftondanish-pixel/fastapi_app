from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, UTC
from models.user import Base

class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False)
    otp  = Column(String(6), nullable=False)
    purpose = Column(String(50), nullable=False)
    full_name = Column(String(255))
    password_hash = Column(String(255))
    account_type = Column(String(50))
    organization_name = Column(String(255))
    retry_count = Column(Integer,default=0)
    expires_at = Column(DateTime)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True),default=lambda: datetime.now(UTC))    
    
    