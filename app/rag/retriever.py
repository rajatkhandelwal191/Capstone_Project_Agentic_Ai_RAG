from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="nomic-embed-text")

db = FAISS.load_local(
    "app/rag/faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)


def query_rag(query):

    docs = db.similarity_search(query, k=4)

    return "\n".join([d.page_content for d in docs])
