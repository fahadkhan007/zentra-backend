from datetime import datetime, timedelta
from jose import jwt # type: ignore
from passlib.context import CryptContext #type: ignore
import secrets

from app.core.redis import redis_client
from app.core.config import settings #type: ignore



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)



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



async def blacklist_token(token: str):
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )

    exp=payload.get("exp")

    if not exp:
        return

    expire_time=exp- int(datetime.utcnow().timestamp())
    if expire_time>0:
        await redis_client.setex(
            name=f"blacklist:{token}",
            time=expire_time,
            value="true"
        )

async def is_token_blacklisted(token: str) -> bool:
    result = await redis_client.get(f"blacklist:{token}")
    return result is not None
