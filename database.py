import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from collections.abc import AsyncGenerator
from dotenv import load_dotenv

load_dotenv()

DB_URL_CONNECT=f"postgresql+psycopg2://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_async_engine(
    DB_URL_CONNECT,
    pool_size = 10,
    max_overflow = 20,
    pool_recycle = 1800,
    pool_pre_ping = True,
    echo = False
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_session()->AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session