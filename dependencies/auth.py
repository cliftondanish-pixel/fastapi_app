from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from models.user import User
from services.jwt_service import decode_token

def get_current_user(
    access_token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(
        status_code=401,
        detail="Not authenticated"
    )
    
    payload = decode_token(access_token)
    
    user_id = payload.get("user_id")
    
    user = db.query(User).filter(
        User.id == user_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
    )
    return user