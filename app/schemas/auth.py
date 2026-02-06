from pydantic import BaseModel, EmailStr
from uuid import UUID

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    
    
class UserLogin(BaseModel):
    email : EmailStr
    password : str
 
 
    
class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    name: str

    class Config:
        from_attribute = True
    

class Token(BaseModel):
    access_token: str
    token_type: str= "bearer"
    
    


class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetComplete(BaseModel):
    token: str
    new_password: str
