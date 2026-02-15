from redis.asyncio import Redis
from app.core.config import settings

redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD and settings.REDIS_PASSWORD != "" else None,
    db=0,
    decode_responses=True
)

redis_client_rag = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD and settings.REDIS_PASSWORD != "" else None,
    db=1,
    decode_responses=True
)

