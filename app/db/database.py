from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings #type: ignore

# Convert PostgreSQL URL to async version (postgresql:// -> postgresql+psycopg://)
DATABASE_URL = str(settings.DATABASE_URL).replace(
    "postgresql://", "postgresql+psycopg://"
)


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

