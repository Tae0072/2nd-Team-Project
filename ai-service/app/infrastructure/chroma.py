import chromadb
from chromadb.config import Settings

_client: chromadb.ClientAPI | None = None
COLLECTION_NAME = "qtai_corpus"


async def init_chroma():
    """ChromaDB 클라이언트 초기화 및 컬렉션 생성"""
    global _client
    _client = chromadb.HttpClient(
        host="chromadb",   # K8s Service DNS
        port=8000,
        settings=Settings(allow_reset=True),
    )
    # 컬렉션 없으면 생성
    _client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    print(f"ChromaDB 초기화 완료 — collection: {COLLECTION_NAME}")


def get_chroma_collection():
    if _client is None:
        raise RuntimeError("ChromaDB 미초기화")
    return _client.get_collection(COLLECTION_NAME)