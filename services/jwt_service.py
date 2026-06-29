from datetime import datetime, timedelta, UTC
from jose import jwt, JWTError
from fastapi import HTTPException
from core.config import settings


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM)

def create_otp_token(email: str):
    expire = datetime.now(UTC) + timedelta(minutes=settings.OTP_TOKEN_EXPIRE_MINUTES)
    payload = {"email": email,"exp": expire}
    return jwt.encode(payload,settings.SECRET_KEY,algorithm=settings.ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=settings.ALGORITHM)
        return payload
    except JWTError as exc:
        raise HTTPException(status_code=401,detail="Invalid or expired token") from exc