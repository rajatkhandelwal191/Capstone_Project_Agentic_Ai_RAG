from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.rag.loaders import load_all_pdfs


def build():

    docs = load_all_pdfs()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    split_docs = splitter.split_documents(docs)

    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )

    db = FAISS.from_documents(split_docs, embeddings)

    db.save_local("app/rag/faiss_index")


if __name__ == "__main__":
    build()