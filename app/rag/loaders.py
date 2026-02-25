from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path

def load_all_pdfs(folder="kb_pdfs"):

    docs = []

    for pdf in Path(folder).glob("*.pdf"):
        loader = PyPDFLoader(str(pdf))
        docs.extend(loader.load())

    return docs