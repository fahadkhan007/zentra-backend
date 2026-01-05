from fastapi import Depends,HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt # type: ignore

from app.db.database import SessionLocal, get_db
from app.core.config import settings
from app.db import models
from sqlalchemy.orm import Session
from app.core.security import is_token_blacklisted

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token:str = Depends(oauth2_scheme),db:Session=Depends(get_db)):
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )
    
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")  # type: ignore
        if user_id is None:
            raise credential_exception
    except JWTError:
        raise credential_exception
    user = db.query(models.User).filter(models.User.email == user_id).first() # type: ignore
    if user is None:
        raise credential_exception
    return user



