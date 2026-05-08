"""chroma.py — ChromaDB 클라이언트
P2 fix: "chromadb:8000" 하드코딩 → CHROMADB_HOST / CHROMADB_PORT 환경변수
"""
import os
import chromadb
from chromadb.config import Settings

_client: chromadb.ClientAPI | None = None
COLLECTION_NAME = "qtai_corpus"

# P2 fix: .env.example 기준 환경변수
_CHROMA_HOST = os.getenv("CHROMADB_HOST", "localhost")
_CHROMA_PORT = int(os.getenv("CHROMADB_PORT", "8000"))


async def init_chroma() -> None:
    """ChromaDB 클라이언트 초기화 및 컬렉션 생성"""
    global _client
    _client = chromadb.HttpClient(
        host=_CHROMA_HOST,
        port=_CHROMA_PORT,
        settings=Settings(allow_reset=True),
    )
    _client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    print(f"ChromaDB 초기화 완료 — {_CHROMA_HOST}:{_CHROMA_PORT}/{COLLECTION_NAME}")


def get_chroma_collection() -> chromadb.Collection:
    if _client is None:
        raise RuntimeError("ChromaDB 미초기화 — lifespan 실행 전 호출됨")
    return _client.get_collection(COLLECTION_NAME)