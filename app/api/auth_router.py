import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db #type: ignore
from app.schemas.auth import PasswordResetComplete, PasswordResetRequest, Token, UserCreate, UserLogin, UserResponse #type: ignore
from app.services.auth_service import create_user, authenticate_user
from app.core.dependencies import get_current_user, oauth2_scheme
from app.db import models #type: ignore
from app.core.security import generate_password_reset_token, token_expiry, blacklist_token
from app.core.hashing import Hash



router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup",response_model=UserResponse)
async def signup(user_data: UserCreate, db: AsyncSession = Depends(get_db)): # type: ignore
    new_user = await create_user(db, user_data) # type: ignore
    return new_user # type: ignore
    
    
@router.post("/login",response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)): # type: ignore
    token = await authenticate_user(db, form_data) # type: ignore
    return token # type: ignore

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    await blacklist_token(token)
    return {"message": "Logged out successfully"}

@router.post("/request-password-reset")
async def request_password_reset(data: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.User).filter(models.User.email == data.email)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # delete old tokens
    old_tokens_result = await db.execute(
        select(models.passwordResetToken).filter(models.passwordResetToken.user_id == user.id)
    )
    for token_obj in old_tokens_result.scalars():
        await db.delete(token_obj)

    token = generate_password_reset_token()
    expiry = token_expiry(15)

    reset_token = models.passwordResetToken(
        user_id=user.id,
        token=token,
        expires_at=expiry
    )
    db.add(reset_token)
    await db.commit()
    await db.refresh(reset_token)
    
    return {
        "message": f"password reset token generated",
        "reset token": token
    }
    
   
    
    
    

@router.post("/reset-password")
async def reset_password(data: PasswordResetComplete, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.passwordResetToken).filter(models.passwordResetToken.token == data.token)
    )
    token_record = result.scalar_one_or_none()

    if not token_record:
        raise HTTPException(status_code=400, detail="Invalid token")

    if datetime.datetime.utcnow() > token_record.expires_at:  # type: ignore
        raise HTTPException(status_code=400, detail="Token expired")

    user_result = await db.execute(
        select(models.User).filter(models.User.id == token_record.user_id)
    )
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = Hash.bcrypt(data.new_password) # type: ignore

    await db.delete(token_record)
    await db.commit()

    return {"message": "Password reset successful"}


@router.get("/me")
async def read_current_user(current_user: models.User = Depends(get_current_user)): 
    return {
        "id": current_user.id,
        "email": current_user.email
    }
