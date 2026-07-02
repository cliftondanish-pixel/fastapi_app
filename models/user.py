from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import (Column, Integer, String, Boolean, DateTime)
from datetime import datetime, UTC
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    account_type = Column(String(50),nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(),default=datetime.now(UTC))
    updated_at = Column(DateTime(),default=datetime.now(UTC),onupdate=datetime.now(UTC))