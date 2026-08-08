from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings #type: ignore

# Normalize DATABASE_URL to the psycopg async dialect.
# Render provides postgres:// (without ql); also handle postgresql:// and already-prefixed URLs.
_raw_db_url = str(settings.DATABASE_URL)
if _raw_db_url.startswith("postgres://"):
    DATABASE_URL = "postgresql+psycopg://" + _raw_db_url[len("postgres://"):]
elif _raw_db_url.startswith("postgresql://"):
    DATABASE_URL = "postgresql+psycopg://" + _raw_db_url[len("postgresql://"):]
elif "+asyncpg://" in _raw_db_url:
    DATABASE_URL = _raw_db_url.replace("+asyncpg://", "+psycopg://")
else:
    DATABASE_URL = _raw_db_url


engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True
)


AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

