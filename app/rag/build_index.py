from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import Settings
from app.core.embeddings import get_embeddings
from app.core.logger import logger
from app.rag.loaders import load_all_pdfs


def build():
    if Settings.USE_CLOUD:
        raise RuntimeError(
            "build_index.py is for local FAISS only. For cloud, run: python -m app.rag.ingest_qdrant"
        )

    docs = load_all_pdfs(Settings.KB_FOLDER)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    split_docs = splitter.split_documents(docs)

    embeddings = get_embeddings()

    db = FAISS.from_documents(split_docs, embeddings)

    db.save_local(Settings.LOCAL_FAISS_PATH)
    logger.info(
        "Built FAISS index | docs=%s | chunks=%s | output=%s",
        len(docs),
        len(split_docs),
        Settings.LOCAL_FAISS_PATH,
    )


if __name__ == "__main__":
    build()
