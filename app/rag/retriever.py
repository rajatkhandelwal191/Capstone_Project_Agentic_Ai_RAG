from qdrant_client import QdrantClient
from langchain_community.vectorstores import FAISS
from langchain_qdrant import QdrantVectorStore

from app.core.config import Settings
from app.core.embeddings import get_embeddings
from app.core.logger import logger

_db = None


def _get_vector_store():
    global _db

    if _db is not None:
        return _db

    embeddings = get_embeddings()
    if Settings.USE_CLOUD:
        Settings.ensure_cloud_vector_config()
        client = QdrantClient(
            url=Settings.QDRANT_URL,
            api_key=Settings.QDRANT_API_KEY,
            timeout=60,
        )
        _db = QdrantVectorStore(
            client=client,
            collection_name=Settings.QDRANT_COLLECTION,
            embedding=embeddings,
        )
        logger.info(
            "retriever=Qdrant | collection=%s | top_k=%s",
            Settings.QDRANT_COLLECTION,
            Settings.RAG_TOP_K,
        )
        return _db

    _db = FAISS.load_local(
        Settings.LOCAL_FAISS_PATH,
        embeddings,
        allow_dangerous_deserialization=True,
    )
    logger.info(
        "retriever=FAISS | index_path=%s | top_k=%s",
        Settings.LOCAL_FAISS_PATH,
        Settings.RAG_TOP_K,
    )
    return _db


def query_rag(query):
    db = _get_vector_store()
    logger.info(
        "retriever=similarity_search | backend=%s | k=%s | query_chars=%s",
        "Qdrant" if Settings.USE_CLOUD else "FAISS",
        Settings.RAG_TOP_K,
        len(query),
    )

    docs = db.similarity_search(query, k=Settings.RAG_TOP_K)
    logger.info("retriever=similarity_search | returned_docs=%s", len(docs))

    return "\n".join([d.page_content for d in docs])
