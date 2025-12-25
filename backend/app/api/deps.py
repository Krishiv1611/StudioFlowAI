from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.config.database import SessionLocal
from app.core.security import ALGORITHM, SECRET_KEY # Assuming these exist or will be defined
from app.models.user_model import User
from app.config.settings import settings

# If security.py doesn't export them, we fall back to settings
SECRET_KEY = settings.SECRET_KEY if hasattr(settings, 'SECRET_KEY') else "TEST_SECRET"
ALGORITHM = "HS256"

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = payload.get("sub")
        
        if token_data is None:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
        
    user = db.query(User).filter(User.email == token_data).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return user
