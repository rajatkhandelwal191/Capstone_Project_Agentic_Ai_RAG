from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from app.core.logger import logger

embeddings = OllamaEmbeddings(model="nomic-embed-text")

db = FAISS.load_local(
    "app/rag/faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)


def query_rag(query):
    logger.info("retriever=FAISS.similarity_search | k=4 | query_chars=%s", len(query))

    docs = db.similarity_search(query, k=4)
    logger.info("retriever=FAISS.similarity_search | returned_docs=%s", len(docs))

    return "\n".join([d.page_content for d in docs])
