from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+aiomysql://qtai:qtai_pass@localhost:3306/ai_db",
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """DB 연결 초기화 (Alembic migration은 별도 실행)"""
    async with engine.begin():
        print("DB 연결 확인 완료")


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session