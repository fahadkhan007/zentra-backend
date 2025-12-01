from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
    
class UserLogin(BaseModel):
    email : EmailStr
    password : str
 
 
    
class UserResponse(BaseModel):
    id: int
    email: EmailStr

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
