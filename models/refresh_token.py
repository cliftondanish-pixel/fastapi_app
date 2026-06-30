from sqlalchemy import (Column, Integer, String, DateTime, ForeignKey)
from datetime import datetime
from models.user import Base

class RefreshToken(Base):
    __tablename__="refresh_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String(500))
    expires_at = Column(DateTime(),nullable=False)
    created_at = Column(DateTime(),default=datetime.utcnow())