from sqlalchemy import (Column, Integer, String, DateTime, ForeignKey)
from datetime import datetime, UTC
from models.user import Base

class Tenant(Base):
    __tablename__ = "tenants"  
    id = Column(Integer,primary_key=True)
    organization_name = Column(String(255),nullable=False)
    owner_user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(50),default="active")
    created_at = Column(DateTime(),default=datetime.now(UTC))
    updated_at = Column(DateTime(),default=datetime.now(UTC) ,onupdate=datetime.now(UTC))