"""database.py — AI Service MySQL 연결
P2 fix: DATABASE_URL → AI_DB_URL (.env.example과 통일)
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# P2 fix: .env.example 기준 AI_DB_URL 사용
AI_DB_URL = os.getenv(
    "AI_DB_URL",
    "mysql+aiomysql://qtai:qtai_pass@localhost:3306/ai_db",
)

engine = create_async_engine(AI_DB_URL, echo=False, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db() -> None:
    """DB 연결 초기화 확인 (Alembic migration은 alembic upgrade head로 별도 실행)"""
    async with engine.connect() as conn:
        await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
    print(f"DB 연결 확인 완료: {AI_DB_URL.split('@')[-1]}")  # 비밀번호 마스킹


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session