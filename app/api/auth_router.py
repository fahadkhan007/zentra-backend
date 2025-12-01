import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from app.db.database import get_db #type: ignore
from app.schemas.auth import PasswordResetComplete, PasswordResetRequest, Token, UserCreate, UserLogin, UserResponse #type: ignore
from app.services.auth_service import create_user, authenticate_user
from app.core.dependencies import get_current_user
from app.db import models #type: ignore
from app.core.security import generate_password_reset_token, token_expiry
from app.core.hashing import Hash
from app.core.email_utils import send_password_reset_email


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup",response_model=UserResponse)
def signup(user_data: UserCreate, db:Session = Depends(get_db)): # type: ignore
    new_user=create_user(db, user_data) # type: ignore
    return new_user # type: ignore
    
    
@router.post("/login",response_model=Token)
def login(user_data: UserLogin, db:Session = Depends(get_db)): # type: ignore
    token=authenticate_user(db, user_data) # type: ignore
    return token # type: ignore

@router.post("/request-password-reset")
def request_password_reset(data: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # delete old tokens
    db.query(models.passwordResetToken).filter(models.passwordResetToken.user_id == user.id).delete()

    token = generate_password_reset_token()
    expiry = token_expiry(15)

    reset_token = models.passwordResetToken(
        user_id=user.id,
        token=token,
        expires_at=expiry
    )
    db.add(reset_token)
    db.commit()
    db.refresh(reset_token)
    
    return {
        "message": f"password reset token generated",
        "reset token": token
    }
    
    #send_password_reset_email(user.email, token)
    #return {"message": "Password reset email sent"}
    # For demonstration, we skip actual email sending
    
    
    

    



@router.post("/reset-password")
def reset_password(data: PasswordResetComplete, db: Session = Depends(get_db)):
    token_record = db.query(models.passwordResetToken)\
        .filter(models.passwordResetToken.token == data.token)\
        .first()

    if not token_record:
        raise HTTPException(status_code=400, detail="Invalid token")

    if datetime.datetime.utcnow() > token_record.expires_at:  # type: ignore
        raise HTTPException(status_code=400, detail="Token expired")

    user = db.query(models.User).filter(models.User.id == token_record.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = Hash.bcrypt(data.new_password) # type: ignore

    db.delete(token_record)
    db.commit()

    return {"message": "Password reset successful"}

@router.get("/me")
def read_current_user(current_user: models.User = Depends(get_current_user)): 
    return {
        "id": current_user.id,
        "email": current_user.email
    }