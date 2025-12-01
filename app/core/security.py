from datetime import datetime, timedelta
from jose import jwt # type: ignore
from passlib.context import CryptContext #type: ignore
import secrets

from app.core.config import settings #type: ignore



# -----------------------------
# 1) Password Hashing (bcrypt)
# -----------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# -----------------------------
# 2) JWT Token Creation
# -----------------------------
def create_access_token(data: dict) -> str:
    
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt

def generate_password_reset_token() -> str:
    return secrets.token_urlsafe(32)

def token_expiry(minutes: int = 15):
    return datetime.utcnow() + timedelta(minutes=minutes)
    
